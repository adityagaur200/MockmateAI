from bson import ObjectId
from fastapi import HTTPException

# 🔹 Convert MongoDB document to JSON serializable
def serialize_mongo(document):
    if not document:
        return None

    document["_id"] = str(document["_id"])
    return document


# 🔹 Serialize list of documents
def serialize_list(documents):
    return [serialize_mongo(doc) for doc in documents]


# 🔹 Safe JSON conversion for Redis
def safe_json(data):
    import json
    try:
        return json.dumps(data)
    except Exception:
        return str(data)
    
# Check for file type 
def validate_file_type(file,allowed_types):
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400,detail="Invalied file type")
    
#Check for file size
def validate_file_size(file,max_size_mb=5):
    file_size = file.spool_max_size
    if file_size > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400,detail="File size exceeds the limit")