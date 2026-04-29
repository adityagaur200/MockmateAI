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


class Skills(BaseModel):
    skill: str
    value: int  # 1-10


class TopicPlan(BaseModel):
    id: str
    topic: str
    priority: int
    depth: str
    why: str


class InterviewPlan(BaseModel):
    candidate_name: str
    role: str
    strengths: List[str] = []
    gaps: List[str] = []
    topics: List[TopicPlan] = []
    suggested_turns: int = 6
    opening_angle: str = ""


class CoverageState(BaseModel):
    covered_ids: List[str] = []
    weak_ids: List[str] = []
    follow_up_counts: dict = {}
    turn_count: int = 0


class Interview(BaseModel):
    user_id: str
    job_name: str
    resume_text: str
    job_description: str
    plan: Optional[InterviewPlan] = None
    coverage: Optional[CoverageState] = None
    history: List[QuestionAnswer] = []
    current_question: Optional[str] = None
    status: str = "IN_PROGRESS"
    created_at: datetime = Field(default_factory=datetime.now)
    skill_radar: Optional[List[Skills]] = []
    final_feedback: Optional[str] = None
    final_score: Optional[float] = None
    hiring_recommendation: Optional[str] = None
    strengths: Optional[List[str]] = []
    areas_to_improve: Optional[List[str]] = []
    ended_at: Optional[datetime] = None

