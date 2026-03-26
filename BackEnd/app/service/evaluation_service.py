from google import genai   # ✅ correct import
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("❌ GEMINI_API_KEY not found. Check your .env file")

client = genai.Client(api_key=api_key)


def evaluate_answer(question, answer):
    prompt = f"""
Evaluate the candidate answer.

Question:
{question}

Answer:
{answer}

Return STRICT JSON:
{{
    "score": number (1-10),
    "feedback": "short feedback"
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    try:
        return json.loads(response.text)
    except Exception as e:
        return {
            "score": 5,
            "feedback": response.text
        }