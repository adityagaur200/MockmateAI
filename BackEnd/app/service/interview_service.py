from datetime import datetime
from http.client import HTTPException
import json
from bson import ObjectId
from app.db.mongodb import interview_collection
from app.db.mongodb import redis_client
from app.service.ai_service import generate_first_question
from app.agents.planner import plan_interview
from app.utils.helpers import serialize_mongo

async def start_interview(user_id, resume_text, job_description, job_name):
    """
    Start a new interview session.
    1. Call planner to create interview plan
    2. Generate first question using the plan
    3. Save interview with plan and coverage to MongoDB
    """

    # 1. Plan the interview (sync call - Gemini API)
    print("Planning interview...")
    plan = plan_interview(resume_text, job_description)
    print(f"Plan created for: {plan.get('candidate_name')}")

    # 2. Generate first question using the plan
    first_question = await generate_first_question(resume_text, job_description, plan)

    if not first_question or not first_question.strip():
        raise ValueError("Failed to generate the first question.")

    # 3. Initialize coverage state
    coverage = {
        "covered_ids": [],
        "weak_ids": [],
        "follow_up_counts": {},
        "turn_count": 0
    }

    # 4. Create interview document
    interview = {
        "job_name": job_name,
        "user_id": user_id,
        "resume_text": resume_text,
        "job_description": job_description,
        "plan": plan,
        "coverage": coverage,
        "history": [],
        "current_question": first_question,
        "status": "IN_PROGRESS",
        "created_at": datetime.utcnow()
    }
    
    try:
        print("Inserting interview into MongoDB...")
        result = await interview_collection.insert_one(interview)
        print(f"Interview inserted with ID: {result.inserted_id}")
        interview_id = str(result.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 5. Cache to Redis
    interview_cache = {
        **interview,
        "_id": interview_id
    }

    print("Setting interview to Redis...")
    redis_client.set(f"interview:{interview_id}", json.dumps(serialize_mongo(interview_cache)), ex=3600)
    print("Redis set completed.")

    print("Preparing to return result...")
    result = {
        "interview_id": interview_id,
        "job_name": job_name,
        "first_question": first_question,
        "created_at": interview["created_at"]
    }
    print("Returning result.")
    return result


async def get_current_question(interview_id):
    """Get the current question for an interview from cache or database."""

    # 🔹 Try Redis first (FAST)
    cached = redis_client.get(f"interview:{interview_id}")

    if cached:
        interview = json.loads(cached)
    else:
        # 🔹 Fallback to MongoDB
        interview = await interview_collection.find_one({"_id": ObjectId(interview_id)})

        if not interview:
            return {"error": "Interview not found"}

        interview = serialize_mongo(interview)

        # 🔹 Cache it
        redis_client.set(
            f"interview:{interview_id}",
            json.dumps(interview),
            ex=3600
        )

    # Stop if completed
    if interview["status"] == "COMPLETED":
        return {
            "status": "COMPLETED",
            "message": "Interview Completed 🎉",
            "final_score": sum([h["score"] for h in interview.get("history", [])]) / len(interview.get("history", [])) if interview.get("history") else 0,
            "total_questions": len(interview.get("history", []))
        }
    
    # ✅ Return only required fields
    return {
        "current_question": interview.get("current_question"),
        "status": interview.get("status"),
        "progress": f"{len(interview.get('history', []))}/{interview.get('plan', {}).get('suggested_turns', 6)}"
    }