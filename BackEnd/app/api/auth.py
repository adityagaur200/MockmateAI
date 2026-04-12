import token
from urllib import response

from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime

from app.db.mongodb import user_collection
from app.auth.utils import hash_password, verify_password, create_access_token
from app.schemas.user_schema import UserRegister, UserLogin, UserResponse
from app.models.user_model import User

router = APIRouter(prefix="/auth", tags=["Auth"])


# ✅ REGISTER
@router.post("/register", response_model=UserResponse)
async def register(user: UserRegister):

    existing_user = await user_collection.find_one({"email": user.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        created_at=datetime.utcnow()
    )

    result = await user_collection.insert_one(new_user.dict())

    created_user = await user_collection.find_one({"_id": result.inserted_id})

    return created_user


# ✅ LOGIN
@router.post("/login")
async def login(user: UserLogin):

    db_user = await user_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "user_id": str(db_user["_id"]),
        "email": db_user["email"]
    })

    response = {
    "access_token": token,
    "token_type": "bearer",
    "user_id": str(db_user["_id"]),
    "name": db_user["name"]
}

    print(f"User logged in: {response}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(db_user["_id"]),
        "name": db_user["name"]
    }