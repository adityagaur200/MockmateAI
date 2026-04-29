import json
import time
import os
import re
from google import genai
from google.genai.errors import ServerError
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def call_llm(prompt: str, retries: int = 3) -> str | None:
    """Make a single LLM call with retry logic."""
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
        except ServerError:
            print(f"⚠️ Gemini 503, retry {attempt + 1}")
            time.sleep(2 ** attempt)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            break
    return None


def extract_json(text: str) -> dict | None:
    """Extract JSON from LLM response, handling markdown blocks."""
    if not text:
        return None
    text = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
    return None


def plan_interview(resume: str, jd: str) -> dict:
    """
    Analyze resume vs JD and create a structured interview plan.
    Runs ONCE when interview starts.
    
    Returns:
    {
        "candidate_name": str,
        "role": str,
        "strengths": ["skill1", ...],
        "gaps": ["gap1", ...],
        "topics": [
            {
                "id": "t1",
                "topic": str,
                "priority": int (1-5),
                "depth": "deep|medium|light",
                "why": str
            }
        ],
        "suggested_turns": int (4-9),
        "opening_angle": str
    }
    """
    prompt = f"""You are an expert technical interviewer planning a structured interview.

CANDIDATE RESUME:
{resume}

JOB DESCRIPTION:
{jd}

## YOUR TASK:
Analyze the candidate's resume against the job description. Create a strategic interview plan.

## RULES:
1. Extract candidate name from resume (or use "Candidate" if not found)
2. Extract target role from JD
3. Identify candidate STRENGTHS (skills they clearly have)
4. Identify GAPS (skills required by JD but missing/weak in resume)
5. Create 4-6 TOPICS to cover, ordered by priority:
   - depth "deep" → candidate claims this skill → dig hard to verify
   - depth "medium" → JD requires it, candidate has some mention
   - depth "light" → JD requires it, candidate doesn't mention
6. Set suggested_turns (4-9): estimate turns needed based on JD complexity
7. Set opening_angle: tone instruction for the first question

## STRICT JSON OUTPUT (ONLY valid JSON, no extra text):
{{
  "candidate_name": "extracted or 'Candidate'",
  "role": "target role from JD",
  "strengths": ["skill1", "skill2"],
  "gaps": ["gap1", "gap2"],
  "topics": [
    {{
      "id": "t1",
      "topic": "topic name",
      "priority": 1,
      "depth": "deep",
      "why": "brief reason"
    }}
  ],
  "suggested_turns": 6,
  "opening_angle": "Start by asking about [specific project or skill]"
}}

IMPORTANT:
- Return ONLY the JSON object, no markdown blocks, no extra text
- All fields must be present
- suggested_turns must be integer between 4 and 9
- Return valid JSON only"""

    response_text = call_llm(prompt, retries=3)
    if not response_text:
        # Fallback: generic plan
        return {
            "candidate_name": "Candidate",
            "role": "Software Engineer",
            "strengths": ["Problem Solving"],
            "gaps": ["System Design"],
            "topics": [
                {
                    "id": "t1",
                    "topic": "Recent Projects",
                    "priority": 1,
                    "depth": "medium",
                    "why": "Understand practical experience"
                },
                {
                    "id": "t2",
                    "topic": "Technical Skills",
                    "priority": 2,
                    "depth": "medium",
                    "why": "Verify core competencies"
                },
                {
                    "id": "t3",
                    "topic": "Problem Solving",
                    "priority": 3,
                    "depth": "medium",
                    "why": "Assess algorithmic thinking"
                },
                {
                    "id": "t4",
                    "topic": "System Design",
                    "priority": 4,
                    "depth": "light",
                    "why": "Evaluate architecture knowledge"
                }
            ],
            "suggested_turns": 6,
            "opening_angle": "Start with a recent project you're proud of"
        }

    plan = extract_json(response_text)
    if not plan:
        # Fallback returned
        return {
            "candidate_name": "Candidate",
            "role": "Software Engineer",
            "strengths": ["Problem Solving"],
            "gaps": ["System Design"],
            "topics": [
                {
                    "id": "t1",
                    "topic": "Recent Projects",
                    "priority": 1,
                    "depth": "medium",
                    "why": "Understand practical experience"
                },
                {
                    "id": "t2",
                    "topic": "Technical Skills",
                    "priority": 2,
                    "depth": "medium",
                    "why": "Verify core competencies"
                },
                {
                    "id": "t3",
                    "topic": "Problem Solving",
                    "priority": 3,
                    "depth": "medium",
                    "why": "Assess algorithmic thinking"
                },
                {
                    "id": "t4",
                    "topic": "System Design",
                    "priority": 4,
                    "depth": "light",
                    "why": "Evaluate architecture knowledge"
                }
            ],
            "suggested_turns": 6,
            "opening_angle": "Start with a recent project you're proud of"
        }

    # Validate suggested_turns is 4-9
    if "suggested_turns" in plan:
        turns = plan["suggested_turns"]
        if not isinstance(turns, int) or turns < 4 or turns > 9:
            plan["suggested_turns"] = 6

    return plan
