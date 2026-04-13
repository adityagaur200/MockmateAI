from datetime import datetime
from http.client import HTTPException
import json
from bson import ObjectId
from app.db.mongodb import interview_collection
from app.db.mongodb import redis_client
from app.service.ai_service import generate_first_question, generate_next_question
from app.service.evaluation_service import evaluate_answer
from app.utils.helpers import serialize_mongo



MAX_QUESTIONS = 2

async def start_interview(user_id, resume_text, job_description,job_name):

    first_question = await generate_first_question(resume_text, job_description)

    if not first_question or not first_question.strip():
        raise ValueError("Failed to generate the first question.")

    interview = {
        "job_name": job_name,
        "user_id": user_id,
        "resume_text": resume_text,
        "job_description": job_description,
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


async def submit_answer(interview_id, answer_text):

    # 🔹 Fetch from Redis first
    cached = redis_client.get(f"interview:{interview_id}")

    if cached:
        interview = json.loads(cached)
    else:
        interview = await interview_collection.find_one({"_id": ObjectId(interview_id)})
        interview = serialize_mongo(interview)

    # 🔹 Early exit if already completed (idempotent)
    if interview.get("status") == "COMPLETED":
        history = interview.get("history", [])
        total_questions = len(history)
        final_score = sum(h["score"] for h in history) / total_questions if total_questions else 0

        return {
            "status": "COMPLETED",
            "message": "Interview Completed 🎉",
            "final_score": final_score,
            "total_questions": total_questions
        }

    # 🔹 Validate current question
    current_question = interview.get("current_question")
    if not current_question:
        return {
            "status": "ERROR",
            "message": "No active question found. Interview might be completed."
        }

    history = interview.get("history", [])

    # 🔹 Evaluate answer (make async if needed)
    evaluation = evaluate_answer(current_question, answer_text)
    score = evaluation["score"]

    # 🔹 Append history
    history_entry = {
        "question": current_question,
        "answer": answer_text,
        "score": score,
        "feedback": evaluation["feedback"]
    }

    history.append(history_entry)
    total_questions = len(history)

    # 🔹 Interview completion check
    if total_questions >= MAX_QUESTIONS:

        final_score = sum(h["score"] for h in history) / total_questions if total_questions else 0

        await interview_collection.update_one(
            {"_id": ObjectId(interview_id)},
            {
                "$set": {
                    "history": history,
                    "status": "COMPLETED",
                    "current_question": None
                }
            }
        )

        interview["history"] = history
        interview["status"] = "COMPLETED"
        interview["current_question"] = None

        redis_client.set(
            f"interview:{interview_id}",
            json.dumps(interview),
            ex=3600
        )

        return {
            "status": "COMPLETED",
            "message": "Interview Completed 🎉",
            "final_score": final_score,
            "total_questions": total_questions
        }

    # 🔹 Generate next question (adaptive logic)
    if score < 5:
        next_question = await generate_next_question(
            interview["resume_text"],
            interview["job_description"],
            history + [{"type": "instruction", "content": "Ask a follow-up question on the same topic"}]
        )

    elif score >= 8:
        next_question = await generate_next_question(
            interview["resume_text"],
            interview["job_description"],
            history + [{"type": "instruction", "content": "Move to a new topic or increase difficulty"}]
        )

    else:
        next_question = await generate_next_question(
            interview["resume_text"],
            interview["job_description"],
            history
        )

    # 🔹 Update DB
    await interview_collection.update_one(
        {"_id": ObjectId(interview_id)},
        {
            "$set": {
                "history": history,
                "current_question": next_question
            }
        }
    )

    # 🔹 Update Redis (IMPORTANT: include history)
    interview["history"] = history
    interview["current_question"] = next_question

    redis_client.set(
        f"interview:{interview_id}",
        json.dumps(serialize_mongo(interview)),
        ex=3600
    )

    # 🔹 Final response
    return {
        "next_question": next_question,
        "score": score,
        "feedback": evaluation["feedback"],
        "progress": f"{total_questions}/{MAX_QUESTIONS}"
    }

async def get_current_question(interview_id):

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

    #Stop if completed
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
        "progress": f"{len(interview.get('history', []))}/10"
    }