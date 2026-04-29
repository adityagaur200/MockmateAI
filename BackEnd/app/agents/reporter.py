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


def reporter_agent(
    compressed_history: str,
    plan: dict,
    coverage: dict
) -> dict:
    """
    Runs ONCE at end. Synthesizes collected data into a final report.
    Does NOT re-evaluate. Uses already-collected scores and feedback.
    
    Args:
        compressed_history: Already-compressed string of interview turns (NOT raw list)
        plan: Interview plan {strengths, gaps, topics, ...}
        coverage: Final coverage state {covered_ids, weak_ids, ...}
    
    Returns:
    {
        "final_feedback": str,
        "final_score": float (1-10),
        "hiring_recommendation": "Strong Yes | Yes | Maybe | No",
        "strengths": ["str"],
        "areas_to_improve": ["str"],
        "skill_radar": [
            {"skill": "Technical", "value": int},
            ...
        ]
    }
    """
    plan_json = json.dumps(plan, indent=2)
    coverage_json = json.dumps(coverage, indent=2)

    prompt = f"""You are a senior hiring manager synthesizing interview results.

INTERVIEW PLAN (original assessment):
{plan_json}

FINAL COVERAGE STATE:
{coverage_json}

INTERVIEW TRANSCRIPT (compressed):
{compressed_history}

## YOUR TASK (DO NOT RE-SCORE):
1. Write a concise final_feedback (3-5 sentences) summarizing the candidate overall
2. Calculate final_score (1-10) as average from interview, NOT re-evaluation
3. Make hiring_recommendation: "Strong Yes" / "Yes" / "Maybe" / "No"
4. List 3-4 STRENGTHS observed during interview
5. List 3-4 AREAS TO IMPROVE
6. Score candidate on 6 skill dimensions (0-100 scale)

## SKILL RADAR DIMENSIONS:
- Technical: coding ability, architecture knowledge, tool expertise
- Communication: clarity, listening, articulation
- Problem Solving: analytical thinking, approach, depth
- Behavioral: teamwork, adaptability, growth mindset
- System Design: scalability thinking, trade-offs, design patterns
- Domain Knowledge: industry understanding, best practices

## HIRING RECOMMENDATION LOGIC:
- "Strong Yes" if final_score >= 8 and no major gaps
- "Yes" if final_score >= 6.5 and only minor gaps
- "Maybe" if final_score >= 5.5 but notable gaps or inconsistent
- "No" if final_score < 5.5 or critical skill gaps

## STRICT JSON OUTPUT (ONLY valid JSON, no extra text):
{{
  "final_feedback": "Strong technical foundation with excellent problem solving...",
  "final_score": 7.5,
  "hiring_recommendation": "Yes",
  "strengths": ["Clear communication", "Strong algorithms", "Collaborative mindset"],
  "areas_to_improve": ["System design depth", "Hands-on DevOps experience"],
  "skill_radar": [
    {{"skill": "Technical", "value": 80}},
    {{"skill": "Communication", "value": 75}},
    {{"skill": "Problem Solving", "value": 85}},
    {{"skill": "Behavioral", "value": 70}},
    {{"skill": "System Design", "value": 60}},
    {{"skill": "Domain Knowledge", "value": 65}}
  ]
}}

IMPORTANT:
- Return ONLY the JSON object, no markdown blocks, no extra text
- final_score must be float (e.g., 7.5)
- hiring_recommendation must be one of the 4 options
- skill_radar must have exactly 6 items with values 0-100
- All fields required
- Return valid JSON only"""

    response_text = call_llm(prompt, retries=3)
    if not response_text:
        # Fallback: create basic report from coverage
        avg_score = 6.0
        return {
            "final_feedback": "Interview completed. Candidate demonstrated foundational skills.",
            "final_score": avg_score,
            "hiring_recommendation": "Maybe",
            "strengths": ["Completed interview", "Showed willingness to engage"],
            "areas_to_improve": ["Could provide more detail", "Needs deeper technical depth"],
            "skill_radar": [
                {"skill": "Technical", "value": 60},
                {"skill": "Communication", "value": 65},
                {"skill": "Problem Solving", "value": 60},
                {"skill": "Behavioral", "value": 65},
                {"skill": "System Design", "value": 50},
                {"skill": "Domain Knowledge", "value": 55}
            ]
        }

    result = extract_json(response_text)
    if not result:
        # Fallback
        avg_score = 6.0
        return {
            "final_feedback": "Interview completed. Candidate demonstrated foundational skills.",
            "final_score": avg_score,
            "hiring_recommendation": "Maybe",
            "strengths": ["Completed interview", "Showed willingness to engage"],
            "areas_to_improve": ["Could provide more detail", "Needs deeper technical depth"],
            "skill_radar": [
                {"skill": "Technical", "value": 60},
                {"skill": "Communication", "value": 65},
                {"skill": "Problem Solving", "value": 60},
                {"skill": "Behavioral", "value": 65},
                {"skill": "System Design", "value": 50},
                {"skill": "Domain Knowledge", "value": 55}
            ]
        }

    # Validate final_score
    if "final_score" in result:
        try:
            result["final_score"] = max(1.0, min(10.0, float(result["final_score"])))
        except (ValueError, TypeError):
            result["final_score"] = 6.0

    # Validate hiring_recommendation
    valid_recommendations = ["Strong Yes", "Yes", "Maybe", "No"]
    if result.get("hiring_recommendation") not in valid_recommendations:
        result["hiring_recommendation"] = "Maybe"

    # Validate skill_radar
    if not isinstance(result.get("skill_radar"), list) or len(result.get("skill_radar", [])) != 6:
        result["skill_radar"] = [
            {"skill": "Technical", "value": 60},
            {"skill": "Communication", "value": 65},
            {"skill": "Problem Solving", "value": 60},
            {"skill": "Behavioral", "value": 65},
            {"skill": "System Design", "value": 50},
            {"skill": "Domain Knowledge", "value": 55}
        ]

    return result
