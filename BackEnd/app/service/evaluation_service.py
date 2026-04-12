import time as time_module
from google.genai.errors import ServerError
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
    "feedback": "short feedback",
    "next_question": "the next question to ask the candidate, or null if interview should end"
}}
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text = response.text.strip()

            # 🔥 Try parsing JSON safely
            try:
                return json.loads(text)
            except:
                # fallback if model returns bad format
                return {
                    "score": 5,
                    "feedback": text,
                    "next_question": "Can you explain your project in more detail?"
                }

        except ServerError as e:
            print(f"⚠️ Gemini 503 error, retry {attempt+1}...")
            time_module.sleep(2 * (attempt + 1))

        except Exception as e:
            print("❌ Unexpected error:", str(e))
            break

    # 🔥 FINAL FALLBACK (VERY IMPORTANT)
    return {
       
        "feedback": "Evaluation skipped due to server issue",
        "next_question": "Tell me about your project architecture."
    }


async def generate_final_feedback(resume, jd, history):
    prompt = f"""
    You are an expert interviewer.

    Resume:
    {resume}

    Job Description:
    {jd}

    Interview History:
    {history}

    Feedback:
    Based on the above, provide a Short and precise final evaluation summary of 4-5 sentences.

    Final Score:
    Based on the above, provide a final score from 1 to 10.


### Instructions:
1. Evaluate the candidate on the following skills:
   - Technical
   - Communication
   - Problem Solving
   - Behavioral
   - System Design
   - Domain Knowledge

2. Give a score from 0 to 100 for each skill.
{{ 
  "skill_radar": [
    {{ "skill": "Technical", "value": number }},
    {{ "skill": "Communication", "value": number }},
    {{ "skill": "Problem Solving", "value": number }},
    {{ "skill": "Behavioral", "value": number }},
    {{ "skill": "System Design", "value": number }},
    {{ "skill": "Domain Knowledge", "value": number }}
  ]
}}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print(response.text.strip())
        return response.text.strip()
    
    except ServerError as e:
        print(f"❌ Error in generate_final_feedback: {e}")
        return "Sorry, I'm having trouble generating feedback right now."