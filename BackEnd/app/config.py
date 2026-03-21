import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "mock_interview"

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")