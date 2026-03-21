from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI
import redis
from app.config import REDIS_URL

client = AsyncIOMotorClient(MONGO_URI)

db = client["MockMateAI"]

interview_collection = db["interviews"]
user_collection = db["users"]

redis_client = redis.StrictRedis.from_url(REDIS_URL)