from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, List

from app.models.interview_model import QuestionAnswer, Skills
from app.utils.ObjectId_Vallidator import PyObjectId


#Start Interview Request
class StartInterviewRequest(BaseModel):
    job_name: str
    job_description: str
    create_at: datetime


#Start Interview Response
class StartInterviewResponse(BaseModel):
    interview_id: str
    job_name: str
    first_question: str
    created_at: datetime


# Submit Answer Request
class SubmitAnswerRequest(BaseModel):
    answer_text: Optional[str] = None


# Submit Answer Response
class SubmitAnswerResponse(BaseModel):
    next_question: str
    score: int
    feedback: str


# Interview Report
class InterviewReportResponse(BaseModel):
    interview_id: str
    job_name: str
    total_questions: int
    average_score: float
    summary: str


class InterviewResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: str
    job_name: str
    resume_text: str
    job_description: str
    history: List[QuestionAnswer] = []
    current_question: Optional[str] = None
    status: str
    created_at: datetime
    final_score: Optional[float] = None
    final_feedback: Optional[str] = None
    ended_at: Optional[datetime] = None
    skill_radar: Optional[List[Skills]] = []
    hiring_recommendation: Optional[str] = None
    strengths: Optional[List[str]] = []
    areas_to_improve: Optional[List[str]] = []
    plan: Optional[dict] = None
    coverage: Optional[dict] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str
        }