from pymongo import MongoClient
from app.config import MONGO_URI

client = MongoClient(MONGO_URI)

db = client["MockMateAI"]

interview_collection_sync = db["interviews"]
user_collection_sync = db["users"]