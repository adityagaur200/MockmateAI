from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Answer(BaseModel):
    answer_text: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    transcript: Optional[str] = None
    score: Optional[int] = None
    feedback: Optional[str] = None


class QuestionAnswer(BaseModel):
    question: str
    answer: Optional[Answer] = None
    created_at: datetime = Field(default_factory=datetime.now)


class Interview(BaseModel):
    user_id: str
    resume_text: str
    job_description: str

    history: List[QuestionAnswer] = []

    current_question: Optional[str] = None

    status: str = "IN_PROGRESS"  

    created_at: datetime = Field(default_factory=datetime.now())