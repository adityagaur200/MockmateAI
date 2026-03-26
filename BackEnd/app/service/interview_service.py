from http.client import HTTPException
import json
from bson import ObjectId
from app.db.mongodb import interview_collection
from app.db.mongodb import redis_client
from app.service.ai_service import generate_first_question, generate_next_question
from app.service.evaluation_service import evaluate_answer
from app.utils.helpers import serialize_mongo

MAX_QUESTIONS = 10
MIN_QUESTIONS = 8


async def start_interview(resume_text, job_description,job_name):

    first_question = await generate_first_question(resume_text, job_description)

    interview = {
        "job_name": job_name,
        "resume_text": resume_text,
        "job_description": job_description,
        "history": [],
        "current_question": first_question,
        "status": "IN_PROGRESS"
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

    redis_client.set(f"interview:{interview_id}", json.dumps(interview_cache), ex=3600)

    return {
        "interview_id": interview_id,
        "job_name": job_name,
        "first_question": first_question
    }


async def submit_answer(interview_id, answer_text):

    cached = redis_client.get(f"interview:{interview_id}")

    if cached:
        interview = json.loads(cached)
    else:
        interview = await interview_collection.find_one({"_id": ObjectId(interview_id)})
        interview = serialize_mongo(interview)

    current_question = interview["current_question"]
    history = interview["history"]

    evaluation = evaluate_answer(current_question, answer_text)
    score = evaluation["score"]

    history_entry = {
        "question": current_question,
        "answer": answer_text,
        "score": score,
        "feedback": evaluation["feedback"]
    }

    history.append(history_entry)
    total_questions = len(history)

    # ✅ Interview completion
    if total_questions >= MAX_QUESTIONS or (total_questions >= MIN_QUESTIONS and score >= 8):

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

        return {
            "message": "Interview Completed 🎉",
            "final_score": sum([h["score"] for h in history]) / total_questions,
            "total_questions": total_questions
        }

    # ✅ Generate next question
    if score < 5:
        next_question = await generate_next_question(
            interview["resume_text"],
            interview["job_description"],
            history + [{"instruction": "Ask a follow-up question on the same topic"}]
        )
    elif score >= 8:
        next_question = await generate_next_question(
            interview["resume_text"],
            interview["job_description"],
            history + [{"instruction": "Move to a new topic or increase difficulty"}]
        )
    else:
        next_question = await generate_next_question(
            interview["resume_text"],
            interview["job_description"],
            history
        )

    # ✅ Update ONLY required fields
    await interview_collection.update_one(
        {"_id": ObjectId(interview_id)},
        {
            "$set": {
                "history": history,
                "current_question": next_question
            }
        }
    )

    # ✅ Update Redis safely
    interview["current_question"] = next_question

    redis_client.set(
        f"interview:{interview_id}",
        json.dumps(serialize_mongo(interview)),
        ex=3600
    )

    return {
        "next_question": next_question,
        "score": score,
        "feedback": evaluation["feedback"],
        "progress": f"{total_questions}/10"
    }