import json
from bson import ObjectId
from app.agents.celery_worker import celery_app
from app.service.transcription_service import transcribe_audio
from app.service.evaluation_service import evaluate_answer
from app.service.ai_service import generate_next_question
from app.db.mongodb import interview_collection
from app.db.mongodb import redis_client


@celery_app.task
def process_audio_answer(interview_id, file_path):
    
    #Get interview
    interview = interview_collection.find_one({"_id": ObjectId(interview_id)})

    if not interview:
        return

    current_question = interview["current_question"]

    #Step 1: Transcribe audio
    transcript = transcribe_audio(file_path)

    #Step 2: Evaluate answer
    evaluation = evaluate_answer(current_question, transcript)

    score = evaluation["score"]

    #Save history
    history_entry = {
        "question": current_question,
        "answer": transcript,
        "score": score,
        "feedback": evaluation["feedback"]
    }

    interview["history"].append(history_entry)

    #Step 3: Generate next question
    next_question = generate_next_question(
        interview["resume_text"],
        interview["job_description"],
        interview["history"]
    )

    interview["current_question"] = next_question

    #Update DB
    interview_collection.update_one(
        {"_id": ObjectId(interview_id)},
        {"$set": interview}
    )

    #Update Redis cache
    redis_client.set(
        f"interview:{interview_id}",
        json.dumps(interview),
        ex=3600
    )

    return {
        "transcript": transcript,
        "score": score,
        "next_question": next_question
    }

