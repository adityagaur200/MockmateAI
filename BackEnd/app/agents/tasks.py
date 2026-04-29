import json
from datetime import datetime
from bson import ObjectId
from app.agents.celery_worker import celery_app
from app.agents.evaluator import evaluator_agent
from app.agents.critic import critic_agent
from app.agents.reporter import reporter_agent
from app.service.transcription_service import transcribe_audio
from app.db.mongo_sync import interview_collection_sync
from app.db.mongodb import redis_client
from app.utils.helpers import (
    serialize_mongo,
    compress_history,
    normalize_skill_radar_list,
    average_skill_radar
)


def parse_json_response(text):
    """Parse JSON response from LLM with cleaning."""
    if not text or not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


@celery_app.task
def process_audio_answer(interview_id, file_path):
    """
    Main orchestrator for processing candidate answers.
    
    Flow:
    1. Transcribe audio
    2. Run EVALUATOR_AGENT (score answer only)
    3. Run CRITIC_AGENT (decide next topic, write question, check if end)
    4. Update coverage state
    5. If end: run REPORTER_AGENT (final report)
    6. Save to MongoDB and Redis
    """

    # ========== SETUP ==========
    interview = interview_collection_sync.find_one({"_id": ObjectId(interview_id)})

    if not interview:
        print("❌ Interview not found")
        return

    interview = serialize_mongo(interview)

    # Guard: already completed
    if interview.get("status") == "COMPLETED":
        print("⚠️ Interview already completed")
        return

    # Get context
    plan = interview.get("plan")
    coverage = interview.get("coverage", {
        "covered_ids": [],
        "weak_ids": [],
        "follow_up_counts": {},
        "turn_count": 0
    })
    history = interview.get("history", [])
    current_question = interview.get("current_question")

    print(f"Processing answer for interview: {interview_id}")
    print(f"Turn count: {coverage['turn_count']}")

    # ========== STEP 1: TRANSCRIBE ==========
    try:
        transcript = transcribe_audio(file_path)
        print(f"✅ Transcribed: {transcript[:100]}...")
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return

    # ========== STEP 2: EVALUATOR AGENT ==========
    print("🔍 Evaluating answer...")
    eval_result = evaluator_agent(current_question, transcript, coverage, plan)
    print(f"   Score: {eval_result.get('score')}/10")
    print(f"   Feedback: {eval_result.get('feedback', 'N/A')}")

    # ========== STEP 3: COMPRESS HISTORY & CRITIC AGENT ==========
    compressed = compress_history(history, max_turns=5)
    
    print("⚖️  Critic reviewing decision...")
    critic_result = critic_agent(eval_result, plan, coverage, compressed)
    print(f"   Adjusted score: {critic_result.get('score_adjusted')}/10")
    print(f"   Approved topic: {critic_result.get('approved_topic_id')}")
    print(f"   Should end: {critic_result.get('should_end')}")

    # ========== STEP 4: UPDATE COVERAGE ==========
    coverage["turn_count"] += 1
    topic_id = critic_result.get("approved_topic_id")
    score = critic_result.get("score_adjusted", eval_result.get("score", 0))

    if topic_id:
        # Track covered vs weak topics
        if score >= 6:
            if topic_id not in coverage["covered_ids"]:
                coverage["covered_ids"].append(topic_id)
                print(f"   ✅ Topic {topic_id} marked as covered")
        else:
            if topic_id not in coverage["weak_ids"]:
                coverage["weak_ids"].append(topic_id)
                print(f"   ⚠️  Topic {topic_id} marked as weak")

        # Track follow-up counts
        counts = coverage.get("follow_up_counts", {})
        counts[topic_id] = counts.get(topic_id, 0) + 1
        coverage["follow_up_counts"] = counts

    # ========== STEP 5: APPEND TO HISTORY ==========
    history_entry = {
        "question": current_question,
        "answer": transcript,
        "score": score,
        "feedback": eval_result.get("feedback", ""),
        "topic_id": topic_id
    }
    history.append(history_entry)
    print(f"   📝 History updated (now {len(history)} turns)")

    # ========== STEP 6: END OR CONTINUE ==========
    update_dict = {
        "history": history,
        "coverage": coverage,
        "status": interview.get("status"),
        "current_question": interview.get("current_question")
    }

    if critic_result.get("should_end"):
        print("🏁 Interview ending...")

        # ========== REPORTER AGENT ==========
        compressed_final = compress_history(history, max_turns=10)
        report = reporter_agent(compressed_final, plan, coverage)
        
        print(f"   Final score: {report.get('final_score')}")
        print(f"   Recommendation: {report.get('hiring_recommendation')}")

        # Average with previous interviews
        skill_radar_current = report.get("skill_radar", [])
        skill_radar_current = normalize_skill_radar_list(skill_radar_current)

        previous_interview = interview_collection_sync.find_one(
            {
                "user_id": interview["user_id"],
                "_id": {"$ne": ObjectId(interview_id)},
                "skill_radar": {"$exists": True, "$ne": []}
            },
            sort=[("created_at", -1)]
        )

        previous_skill_radar = []
        if previous_interview:
            previous_skill_radar = previous_interview.get("skill_radar", [])

        averaged_skill_radar = average_skill_radar(skill_radar_current, previous_skill_radar)

        # Update completion fields
        update_dict.update({
            "status": "COMPLETED",
            "current_question": None,
            "final_feedback": report.get("final_feedback"),
            "final_score": report.get("final_score"),
            "skill_radar": averaged_skill_radar,
            "hiring_recommendation": report.get("hiring_recommendation"),
            "strengths": report.get("strengths", []),
            "areas_to_improve": report.get("areas_to_improve", []),
            "ended_at": datetime.utcnow()
        })

    else:
        # Continue: set next question
        next_question = critic_result.get("next_question")
        update_dict["current_question"] = next_question
        update_dict["status"] = "IN_PROGRESS"
        print(f"   ➡️  Next question set")

    # ========== STEP 7: SAVE TO MONGODB ==========
    interview_collection_sync.update_one(
        {"_id": ObjectId(interview_id)},
        {"$set": update_dict}
    )
    print("✅ MongoDB updated")

    # ========== STEP 8: UPDATE REDIS CACHE ==========
    interview.update(update_dict)
    redis_client.set(
        f"interview:{interview_id}",
        json.dumps(serialize_mongo(interview)),
        ex=3600
    )
    print("✅ Redis updated")

    # ========== RETURN ==========
    return {
        "transcript": transcript,
        "score": score,
        "next_question": update_dict.get("current_question"),
        "status": update_dict.get("status"),
        "final_feedback": update_dict.get("final_feedback") if update_dict.get("status") == "COMPLETED" else None,
        "final_score": update_dict.get("final_score") if update_dict.get("status") == "COMPLETED" else None,
        "skill_radar": update_dict.get("skill_radar") if update_dict.get("status") == "COMPLETED" else None
    }