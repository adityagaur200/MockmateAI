from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime


def serialize_mongo(data):
    """Recursively convert MongoDB ObjectId, datetime, and bytes to JSON-safe values."""
    if data is None:
        return None

    if isinstance(data, ObjectId):
        return str(data)

    if isinstance(data, datetime):
        return data.isoformat()

    if isinstance(data, dict):
        out = {}
        for key, value in data.items():
            out[key] = serialize_mongo(value)
        return out

    if isinstance(data, list):
        return [serialize_mongo(item) for item in data]

    # FastAPI's JSON encoder can handle most simple types, but bytes and others may need conversion.
    if isinstance(data, bytes):
        return data.decode("utf-8", errors="replace")

    return data


def serialize_list(documents):
    return [serialize_mongo(doc) for doc in documents]


# Safe JSON conversion for Redis
def safe_json(data):
    import json
    try:
        return json.dumps(data)
    except Exception:
        return str(data)


# Check for file type
def validate_file_type(file, allowed_types):
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")


# Check for file size
def validate_file_size(file, max_size_mb=5):
    content = file.file.read()
    file_size = len(content)
    file.file.seek(0)

    if file_size > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds the limit of 5MB")