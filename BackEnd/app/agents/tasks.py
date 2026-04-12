import asyncio
import datetime
import json
from bson import ObjectId
from app.agents.celery_worker import celery_app
from app.service.transcription_service import transcribe_audio
from app.service.evaluation_service import evaluate_answer, generate_final_feedback
from app.service.ai_service import generate_next_question
from app.db.mongo_sync import interview_collection_sync
from app.db.mongodb import redis_client
from app.utils.helpers import serialize_mongo

MAX_QUESTIONS = 2


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
                "ended_at": end_at if status == "COMPLETED" else None,
                "final_feedback": final_feedback if status == "COMPLETED" else None,
                "final_score": sum([h["score"] for h in interview["history"]]) / len(interview["history"]) if interview["history"] else None
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
        "final_feedback": final_feedback if status == "COMPLETED" else None,
        "final_score": sum([h["score"] for h in interview["history"]]) / len(interview["history"]) if interview["history"] else None
    }