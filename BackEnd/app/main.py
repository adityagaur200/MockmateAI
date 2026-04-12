from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import interview, media, auth
from app.auth.utils import get_current_user


app = FastAPI(title="AI Mock Interview Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROUTES
app.include_router(auth.router)                     
app.include_router(interview.router, prefix="/interview")
app.include_router(media.router, prefix="/media")


@app.get("/")
async def root():
    return {"message": "Backend running 🚀"}