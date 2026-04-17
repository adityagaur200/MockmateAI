import asyncio
from datetime import datetime
import json
from bson import ObjectId
from sympy import re
from app.agents.celery_worker import celery_app
from app.service.transcription_service import transcribe_audio
from app.service.evaluation_service import evaluate_answer, generate_final_feedback
from app.service.ai_service import generate_next_question
from app.db.mongo_sync import interview_collection_sync
from app.db.mongodb import redis_client
from app.utils.helpers import serialize_mongo

MAX_QUESTIONS = 2


def clean_llm_response(text):
    if not text:
        return None
    
    text=re.sub(r"```json|```", "", text).strip()
    return text

def parse_json_response(text):
    if not text or not isinstance(text, str):
        return None

    try:
        cleaned_text = clean_llm_response(text)
        parsed = json.loads(cleaned_text)

        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        return parsed
    except Exception:
        return None


def normalize_skill_radar_list(skill_radar):
    if not isinstance(skill_radar, list):
        return []

    normalized = []
    for item in skill_radar:
        if not isinstance(item, dict):
            continue

        skill = item.get("skill")
        value = item.get("value")
        if skill is None or value is None:
            continue

        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            continue

        normalized.append({"skill": skill, "value": numeric_value})

    return normalized


def average_skill_radar(current_radar, previous_radar):
    current = normalize_skill_radar_list(current_radar)
    previous = normalize_skill_radar_list(previous_radar)

    if not previous:
        return current

    prev_map = {item["skill"]: item["value"] for item in previous}
    current_map = {item["skill"]: item["value"] for item in current}
    all_skills = set(prev_map) | set(current_map)

    averaged = []
    for skill in sorted(all_skills):
        current_value = current_map.get(skill)
        previous_value = prev_map.get(skill)

        if current_value is not None and previous_value is not None:
            value = round((current_value + previous_value) / 2, 2)
        elif current_value is not None:
            value = round(current_value, 2)
        else:
            value = round(previous_value, 2)

        averaged.append({"skill": skill, "value": value})

    return averaged


@celery_app.task
def process_audio_answer(interview_id, file_path):

    # 🔹 Fetch interview
    interview = interview_collection_sync.find_one({"_id": ObjectId(interview_id)})

    if not interview:
        print("❌ Interview not found")
        return

    interview = serialize_mongo(interview)

    # 🚨 1. BLOCK if already completed
    if interview.get("status") == "COMPLETED":
        print("⚠️ Interview already completed")
        end_at=datetime.utcnow();
        return

    # 🚨 2. BLOCK if already max reached (safety)
    if len(interview.get("history", [])) >= MAX_QUESTIONS:
        print("⚠️ Max questions already reached")

        interview_collection_sync.update_one(
            {"_id": ObjectId(interview_id)},
            {"$set": {"status": "COMPLETED", "current_question": None}}
        )
        return

    current_question = interview.get("current_question")

    # 🔹 Step 1: Transcribe
    transcript = transcribe_audio(file_path)
    print("Transcript:", transcript)

    # 🔹 Step 2: Evaluate
    evaluation = evaluate_answer(current_question, transcript)
    score = evaluation["score"]

    # 🔹 Step 3: Append history (IMPORTANT: always append)
    history_entry = {
        "question": current_question,
        "answer": transcript,
        "score": score,
        "feedback": evaluation["feedback"]
    }

    interview["history"].append(history_entry)


    # 🔹 Step 4: Decide next step
    if len(interview["history"]) >= MAX_QUESTIONS:

        final_feedback = asyncio.run(
            generate_final_feedback(
                interview["resume_text"],
                interview["job_description"],
                interview["history"]
            )
        )

        parsed_feedback = parse_json_response(final_feedback)

        if parsed_feedback:
            interview["final_feedback"] = parsed_feedback.get("final_feedback")
            interview["final_score"] = parsed_feedback.get("final_score")
            skill_radar_current = parsed_feedback.get("skill_radar")
        else:
            interview["final_feedback"] = final_feedback
            interview["final_score"] = None
            skill_radar_current = None
        skill_radar_current = parsed_feedback.get("skill_radar") if parsed_feedback and isinstance(parsed_feedback.get("skill_radar"), list) else None

        previous_interview = interview_collection_sync.find_one(
            {
                "user_id": interview["user_id"],
                "_id": {"$ne": ObjectId(interview_id)},
                "skill_radar": {"$exists": True, "$ne": []}
            },
            sort=[("created_at", -1)]
        )

        if skill_radar_current is not None:
            averaged_skill_radar = average_skill_radar(
                skill_radar_current,
                previous_interview.get("skill_radar") if previous_interview else []
            )
        else:
            averaged_skill_radar = previous_interview.get("skill_radar") if previous_interview else []

        interview["skill_radar"] = averaged_skill_radar
        interview["final_feedback"] = parsed_feedback.get("final_feedback") if parsed_feedback else final_feedback

        next_question = None
        status = "COMPLETED"
    else:
        next_question = asyncio.run(
            generate_next_question(
                interview["resume_text"],
                interview["job_description"],
                interview["history"]
            )
        )
        status = "IN_PROGRESS"

    interview["current_question"] = next_question
    interview["status"] = status

    # 🔹 Step 5: Update DB
    interview_collection_sync.update_one(
        {"_id": ObjectId(interview_id)},
        {
            "$set": {
                "current_question": next_question,
                "history": interview["history"],
                "status": status,
                "ended_at": datetime.utcnow() if status == "COMPLETED" else None,
                "final_feedback": interview.get("final_feedback") if status == "COMPLETED" else None,
                "final_score": interview.get("final_score") if status == "COMPLETED" else None,
                "skill_radar": interview.get("skill_radar") if status == "COMPLETED" else interview.get("skill_radar")
            }
        }
    )

    print("✅ Interview updated")
    print("Next question:", next_question)

    # 🔹 Step 6: Update Redis
    redis_client.set(
        f"interview:{interview_id}",
        json.dumps(serialize_mongo(interview)),
        ex=3600
    )

    return {
        "transcript": transcript,
        "score": score,
        "next_question": next_question,
        "status": status,
        "final_feedback": interview.get("final_feedback") if status == "COMPLETED" else None,
        "final_score": interview.get("final_score") if status == "COMPLETED" else None,
        "skill_radar": interview.get("skill_radar") if status == "COMPLETED" else None
    }