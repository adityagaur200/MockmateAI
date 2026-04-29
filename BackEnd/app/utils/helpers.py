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


def compress_history(history: list, max_turns: int = 5) -> str:
    """Compress interview history to last N turns as a formatted string for LLM context."""
    recent = history[-max_turns:]
    lines = []
    for i, turn in enumerate(recent, 1):
        lines.append(
            f"Q{i}: {turn.get('question', '')}\n"
            f"A{i}: {turn.get('answer', '')}\n"
            f"Score: {turn.get('score', 'N/A')}/10\n"
            f"Feedback: {turn.get('feedback', '')}"
        )
    return "\n\n".join(lines)


def normalize_skill_radar_list(skill_radar):
    """Normalize skill radar list to ensure consistent format."""
    if not isinstance(skill_radar, list):
        return []

    normalized = []
    for item in skill_radar:
        if not isinstance(item, dict):
            continue

        skill = item.get("skill")
        value = item.get("value")
        if skill is None or value is None:
            continue

        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            continue

        normalized.append({"skill": skill, "value": numeric_value})

    return normalized


def average_skill_radar(current_radar, previous_radar):
    """Average current skill radar with previous interview radar."""
    current = normalize_skill_radar_list(current_radar)
    previous = normalize_skill_radar_list(previous_radar)

    if not previous:
        return current

    prev_map = {item["skill"]: item["value"] for item in previous}
    current_map = {item["skill"]: item["value"] for item in current}
    all_skills = set(prev_map) | set(current_map)

    averaged = []
    for skill in sorted(all_skills):
        current_value = current_map.get(skill)
        previous_value = prev_map.get(skill)

        if current_value is not None and previous_value is not None:
            value = round((current_value + previous_value) / 2, 2)
        elif current_value is not None:
            value = round(current_value, 2)
        else:
            value = round(previous_value, 2)

        averaged.append({"skill": skill, "value": value})

    return averaged