import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from app.auth.utils import get_current_user
from app.agents.tasks import process_audio_answer
from app.schemas.interview_schema import StartInterviewResponse
from app.service.interview_service import get_current_question, start_interview
from app.utils.file_parser import extract_text_from_pdf
from app.utils.helpers import validate_file_type, validate_file_size
from app.utils.constants import ALLOWED_RESUME_TYPES as allowed_types 
from app.db.mongodb import interview_collection
from bson import ObjectId
from app.utils.helpers import serialize_mongo

router = APIRouter()

#Start Interview
@router.post("/start", response_model=StartInterviewResponse)
async def start(
    user=Depends(get_current_user),
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    job_name: str = Form(...)
):
    try:
        # Validate file type
        validate_file_type(resume,allowed_types)

        # Validate file size
        validate_file_size(resume,max_size_mb=5)

        # Extract resume text
        resume_text = await extract_text_from_pdf(resume)

        # Start interview
        result = await start_interview(user, resume_text, job_description,job_name)

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message":"Interview Start Failed", "error": str(e)})


#Submit answer
@router.post("/{interview_id}/answer")
async def answer(
    interview_id: str,
    file: UploadFile = File(...)
):
    try:
        # ✅ create temp folder if not exists
        os.makedirs("temp", exist_ok=True)

        # ✅ save file locally
        file_location = f"temp/{file.filename}"

        with open(file_location, "wb") as f:
            f.write(await file.read())

        # ✅ send to celery worker
        process_audio_answer.delay(interview_id, file_location)

        return {"message": "Processing answer..."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{interview_id}/question")
async def get_next_question(interview_id: str):
    try:
        result = await get_current_question(interview_id)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard(user=Depends(get_current_user)):

    # Get user_id from JWT
    user_id = user["user_id"]

    interviews = await interview_collection.find({
        "user_id.user_id": user_id
    }).to_list(length=None)

    total_interviews = len(interviews)

    total_score = 0
    total_questions = 0
    total_time = 0

    recent_interviews = []

    for interview in interviews:
        history = interview.get("history", [])

        total_score += sum(q.get("score", 0) for q in history)
        total_questions += len(history)
        
        # Calculate duration from created_at and ended_at
        duration_seconds = 0
        created_at = interview.get("created_at")
        ended_at = interview.get("ended_at")
        if created_at and ended_at:
            duration_seconds = (ended_at - created_at).total_seconds()
        
        # If no ended_at, use duration field as fallback
        if duration_seconds == 0:
            duration_seconds = interview.get("duration", 0)
        
        total_time += duration_seconds

        final_score = interview.get("final_score")
        if final_score is None:
            final_score = round(
                sum(q.get("score", 0) for q in history) / len(history), 1
            ) if history else 0

        recent_interviews.append({
            "id": str(interview["_id"]),
            "job_name": interview.get("job_name", ""),
            "job_description": interview.get("job_description", ""),
            "status": interview.get("status", ""),
            "date": str(interview.get("created_at", "")),
            "score": final_score,
            "final_feedback": interview.get("final_feedback", ""),
            "history_count": len(history)
        })

    avg_score = round(total_score / total_questions, 1) if total_questions else 0

    # Calculate average skill radar from all interviews
    skill_map = {}
    for interview in interviews:
        if interview.get("skill_radar"):
            for skill_item in interview.get("skill_radar", []):
                skill_name = skill_item.get("skill", "Unknown")
                skill_value = skill_item.get("value", 0)
                
                if skill_name not in skill_map:
                    skill_map[skill_name] = {"sum": 0, "count": 0}
                
                skill_map[skill_name]["sum"] += skill_value
                skill_map[skill_name]["count"] += 1
    
    # Calculate averages
    averaged_skill_radar = []
    for skill, values in skill_map.items():
        avg_value = round(values["sum"] / values["count"], 1) if values["count"] > 0 else 0
        averaged_skill_radar.append({"skill": skill, "value": avg_value})

    return {
        "total_interviews": total_interviews,
        "avg_score": avg_score,
        "total_time": round(total_time / 3600, 1),
        "recent_interviews": recent_interviews[-5:][::-1],
        "skill_radar": averaged_skill_radar
    }


@router.get("/{interview_id}")
async def get_interview_details(interview_id: str, user=Depends(get_current_user)):
    try:
        # Get user_id from JWT
        user_id = user["user_id"]

        # Fetch interview by ID
        interview = await interview_collection.find_one({"_id": ObjectId(interview_id)})

        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")

        # Verify user ownership
        interview_user_id = interview.get("user_id", {})
        if isinstance(interview_user_id, dict):
            interview_user_id = interview_user_id.get("user_id")

        if interview_user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Serialize and return
        interview = serialize_mongo(interview)
        return interview

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#Health Check
@router.get("/")
async def test():
    return {"message": "Interview API working 🚀"}