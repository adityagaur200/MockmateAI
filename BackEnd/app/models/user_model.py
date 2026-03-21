from datetime import datetime
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    name: str
    email: EmailStr
    password: str

    created_at: datetime = datetime.utcnow()