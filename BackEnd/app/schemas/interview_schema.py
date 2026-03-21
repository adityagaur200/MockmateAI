from pydantic import BaseModel
from typing import Optional, List


# 🔹 Start Interview Request
class StartInterviewRequest(BaseModel):
    job_description: str


# 🔹 Start Interview Response
class StartInterviewResponse(BaseModel):
    interview_id: str
    first_question: str


# 🔹 Submit Answer Request
class SubmitAnswerRequest(BaseModel):
    answer_text: Optional[str] = None


# 🔹 Submit Answer Response
class SubmitAnswerResponse(BaseModel):
    next_question: str
    score: int
    feedback: str


# 🔹 Interview Report
class InterviewReportResponse(BaseModel):
    interview_id: str
    total_questions: int
    average_score: float
    summary: str