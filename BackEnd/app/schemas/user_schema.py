from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from app.utils.ObjectId_Vallidator import PyObjectId


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: PyObjectId=Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: str

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}