from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.service.interview_service import start_interview, submit_answer
from app.utils.file_parser import extract_text_from_pdf
from app.utils.helpers import validate_file_type, validate_file_size
from app.utils.constants import ALLOWED_RESUME_TYPES as allowed_types 

router = APIRouter()

#Start Interview (Resume + JD)
@router.post("/start")
async def start(
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
        result = await start_interview(resume_text, job_description,job_name)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Submit Answer (Text-based)
@router.post("/{interview_id}/answer")
async def answer(
    interview_id: str,
    answer_text: str = Form(...)
):
    try:
        result = await submit_answer(interview_id, answer_text)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Health Check
@router.get("/")
async def test():
    return {"message": "Interview API working 🚀"}