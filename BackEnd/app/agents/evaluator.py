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


def evaluator_agent(
    question: str,
    answer: str,
    coverage: dict,
    plan: dict
) -> dict:
    """
    Score THIS answer only. Does NOT generate the next question.
    That's the critic's job.
    
    Args:
        question: The question asked
        answer: The candidate's answer
        coverage: Current coverage state {covered_ids, weak_ids, follow_up_counts, turn_count}
        plan: Interview plan {topics, ...}
    
    Returns:
    {
        "score": int (1-10),
        "feedback": str (1-2 sentences),
        "addressed_topic_id": str or null,
        "proposed_next_topic_id": str or null
    }
    """
    topics_json = json.dumps(plan.get("topics", []), indent=2)
    coverage_json = json.dumps(coverage, indent=2)

    prompt = f"""You are an expert answer evaluator for technical interviews.

INTERVIEW PLAN TOPICS:
{topics_json}

CURRENT COVERAGE STATE:
{coverage_json}

CANDIDATE'S QUESTION:
{question}

CANDIDATE'S ANSWER:
{answer}

## YOUR TASK:
1. Score this answer 1-10 based on clarity, accuracy, and depth
2. Write 1-2 sentences of specific feedback
3. Identify which topic ID (t1, t2, etc.) this answer addresses
4. Propose which topic to cover next (the evaluator's suggestion; critic may override)

## SCORING GUIDE:
- 1-3: Vague, incorrect, or off-topic
- 4-5: Basic understanding but weak execution
- 6-7: Good answer, mostly complete and accurate
- 8-9: Excellent answer with depth and examples
- 10: Outstanding answer with exceptional clarity and insight

## STRICT JSON OUTPUT (ONLY valid JSON, no extra text):
{{
  "score": 7,
  "feedback": "Clear explanation with good examples.",
  "addressed_topic_id": "t1",
  "proposed_next_topic_id": "t2"
}}

IMPORTANT:
- Return ONLY the JSON object, no markdown blocks, no extra text
- score must be integer 1-10
- addressed_topic_id must be one of the topic IDs in INTERVIEW PLAN TOPICS or null
- proposed_next_topic_id should be the NEXT uncovered topic or null
- Return valid JSON only"""

    response_text = call_llm(prompt, retries=3)
    if not response_text:
        # Fallback
        return {
            "score": 0,
            "feedback": "Evaluation failed due to server error.",
            "addressed_topic_id": None,
            "proposed_next_topic_id": None
        }

    result = extract_json(response_text)
    if not result:
        # Fallback
        return {
            "score": 0,
            "feedback": "Evaluation failed to parse response.",
            "addressed_topic_id": None,
            "proposed_next_topic_id": None
        }

    # Validate and normalize
    if "score" in result:
        try:
            result["score"] = max(1, min(10, int(result["score"])))
        except (ValueError, TypeError):
            result["score"] = 0

    return result
