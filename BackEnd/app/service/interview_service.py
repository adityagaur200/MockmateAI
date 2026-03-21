import json
from bson import ObjectId
from app.db.mongodb import interview_collection
from app.db.mongodb import redis_client
from app.service.ai_service import generate_first_question, generate_next_question
from app.service.evaluation_service import evaluate_answer


MAX_QUESTIONS = 10
MIN_QUESTIONS = 8


# 🔹 Start Interview
async def start_interview(resume_text, job_description):

    first_question = await generate_first_question(resume_text, job_description)

    interview = {
        "resume_text": resume_text,
        "job_description": job_description,
        "history": [],
        "current_question": first_question,
        "status": "IN_PROGRESS"
    }

    result = await interview_collection.insert_one(interview)
    interview_id = str(result.inserted_id)

    redis_client.set(f"interview:{interview_id}", json.dumps(interview), ex=3600)

    return {
        "interview_id": interview_id,
        "question": first_question
    }


# 🔹 Submit Answer (🔥 SMART VERSION)
async def submit_answer(interview_id, answer_text):

    # 🔹 Get interview
    cached = redis_client.get(f"interview:{interview_id}")

    if cached:
        interview = json.loads(cached)
    else:
        interview = await interview_collection.find_one({"_id": ObjectId(interview_id)})

    current_question = interview["current_question"]
    history = interview["history"]

    # 🔹 Evaluate answer
    evaluation = evaluate_answer(current_question, answer_text)
    score = evaluation["score"]

    # 🔹 Save history
    history_entry = {
        "question": current_question,
        "answer": answer_text,
        "score": score,
        "feedback": evaluation["feedback"]
    }

    history.append(history_entry)

    total_questions = len(history)

    # 🔥 INTERVIEW END CONDITION
    if total_questions >= MAX_QUESTIONS or (total_questions >= MIN_QUESTIONS and score >= 8):
        interview["status"] = "COMPLETED"
        interview["current_question"] = None

        await interview_collection.update_one(
            {"_id": ObjectId(interview_id)},
            {"$set": interview}
        )

        redis_client.set(f"interview:{interview_id}", json.dumps(interview), ex=3600)

        return {
            "message": "Interview Completed 🎉",
            "final_score": sum([h["score"] for h in history]) / total_questions,
            "total_questions": total_questions
        }

    # 🔥 DECIDE NEXT QUESTION TYPE

    if score < 5:
        # 👉 Follow-up question
        next_question = await generate_next_question(
            interview["resume_text"],
            interview["job_description"],
            history + [{"instruction": "Ask a follow-up question on the same topic"}]
        )

    elif score >= 8:
        # 👉 Move to new topic
        next_question = await generate_next_question(
            interview["resume_text"],
            interview["job_description"],
            history + [{"instruction": "Move to a new topic or increase difficulty"}]
        )

    else:
        # 👉 Normal progression
        next_question = await generate_next_question(
            interview["resume_text"],
            interview["job_description"],
            history
        )

    # 🔹 Update interview
    interview["current_question"] = next_question

    await interview_collection.update_one(
        {"_id": ObjectId(interview_id)},
        {"$set": interview}
    )

    redis_client.set(f"interview:{interview_id}", json.dumps(interview), ex=3600)

    return {
        "next_question": next_question,
        "score": score,
        "feedback": evaluation["feedback"],
        "progress": f"{total_questions}/10"
    }