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

def critic_agent(
    eval_result: dict,
    plan: dict,
    coverage: dict,
    compressed_history: str
) -> dict:

    topics_json = json.dumps(plan.get("topics", []), indent=2)
    coverage_json = json.dumps(coverage, indent=2)
    suggested_turns = plan.get("suggested_turns", 6)
    hard_cap = suggested_turns + 2
    turn_count = coverage.get("turn_count", 0)
    candidate_name = plan.get("candidate_name", "the candidate")
    role = plan.get("role", "")
    strengths = plan.get("strengths", [])
    gaps = plan.get("gaps", [])

    # Build topic lookup for critic context
    topic_map = {t["id"]: t for t in plan.get("topics", [])}
    proposed_id = eval_result.get("proposed_next_topic_id")
    proposed_topic = topic_map.get(proposed_id, {})

    prompt = f"""You are the lead interviewer reviewing your junior interviewer's decisions.
You are interviewing {candidate_name} for a {role} role.

## CANDIDATE PROFILE
Strengths (from resume): {', '.join(strengths) if strengths else 'not identified'}
Gaps vs JD: {', '.join(gaps) if gaps else 'not identified'}

## INTERVIEW PLAN
{topics_json}

## CURRENT COVERAGE STATE
{coverage_json}

Turn count: {turn_count} | Suggested turns: {suggested_turns} | Hard cap: {hard_cap}

## RECENT CONVERSATION
{compressed_history}

## JUNIOR INTERVIEWER'S DECISION TO REVIEW
Score given: {eval_result.get('score', 0)}/10
Topic addressed: {eval_result.get('addressed_topic_id', 'unknown')}
Feedback given: {eval_result.get('feedback', '')}
Proposed next topic: {proposed_id} → {proposed_topic.get('topic', 'unknown')} 
  (depth: {proposed_topic.get('depth', 'unknown')}, why: {proposed_topic.get('why', '')})

## YOUR DECISION RULES

### On scoring:
- Score 1-3: Answer was vague, wrong, or showed no real understanding
- Score 4-6: Answer was partial — knew the concept but missed depth or specifics  
- Score 7-8: Solid answer with real examples and good technical detail
- Score 9-10: Exceptional — showed deep mastery, edge cases, real-world nuance
- Adjust the score if the junior interviewer clearly over/underscored
- If the candidate gave a textbook answer with no real example → cap at 6
- If the candidate showed genuine depth with specifics → floor at 7

### On topic selection:
- If follow_up_counts[topic] >= 2 AND score < 6 → confirmed gap, MOVE ON
- If score < 6 AND follow_up_counts[topic] < 2 → follow up on same topic
- If score >= 7 → move to next highest-priority uncovered topic
- NEVER revisit a topic already in covered_ids with score >= 7
- Always prefer higher priority number (priority 1 is most important)

### On ending:
- NEVER end before turn 4 (minimum)
- MUST end at turn {hard_cap} (hard cap, no exceptions)
- Consider ending when ALL of these are true:
  * turn_count >= suggested_turns
  * All priority-1 and priority-2 topics are either covered or confirmed gaps
  * No remaining topics with depth "deep" are untested

## NEXT QUESTION WRITING — THIS IS CRITICAL

You must write the next question like a real senior engineer talking to a candidate.

### Style rules (every violation = bad interview):
✅ ONE sentence maximum
✅ Specific to this candidate's actual background — use their project names,
   tech stack, decisions they made
✅ Natural openers: "How did you...", "What was...", "Walk me through...",
   "Why did you...", "Tell me about...", "What's your approach to..."
✅ If depth is "deep" → ask something that exposes whether they truly did it
   or just listed it on their resume
✅ If following up on a weak answer → probe the specific gap, don't just 
   ask the same question differently

❌ NEVER start with "Given your background..."
❌ NEVER start with "Your profile/resume mentions..."
❌ NEVER start with "Based on your experience..."
❌ NEVER start with "Could you elaborate on..."
❌ NEVER start with "Could you walk me through..."
❌ NEVER put a setup sentence before the question
❌ NEVER ask two things in one question
❌ NEVER use corporate language: "leverage", "utilize", "elaborate on"

### Examples by scenario:

FOLLOWING UP on a weak answer (score < 6):
Previous Q: "How do you handle auth between services?"
Weak answer: "We use JWT tokens"
✅ GOOD follow-up: "How do you handle token expiry when a request is mid-flight between services?"
✅ GOOD follow-up: "What happens when a downstream service rejects a token — how does that surface to the user?"
❌ BAD follow-up: "Could you elaborate more on your JWT implementation approach?"

MOVING TO a new topic (score >= 7):
Moving to System Design (depth: deep):
✅ "If SynQ needs to handle 100k concurrent WebSocket connections, what breaks first?"
✅ "How would you redesign LinkXpert's auth service if it needs to handle 10x the load?"
❌ "Your experience with system design is impressive. Could you describe a system you designed?"

MOVING TO behavioral (depth: light):
✅ "Tell me about a time you disagreed with a technical decision your team made."
✅ "What's a mistake you made on one of these projects and what did you learn?"
❌ "Given your collaborative experience, describe a challenging team situation."

CONFIRMING a gap (moving past a topic the candidate clearly doesn't know):
✅ "Alright, let's shift — walk me through how you think about database indexing."
✅ "Fair enough — tell me how you'd approach debugging a memory leak in production."

## OUTPUT FORMAT — STRICT JSON ONLY

Return ONLY this JSON. No markdown. No explanation. No extra text.

{{
  "score_adjusted": <integer 1-10>,
  "score_change_reason": "<why you changed the score, or null>",
  "approved_topic_id": "<topic id like t1, t2, etc. — must exist in the plan>",
  "override_reason": "<why you overrode the junior's topic choice, or null>",
  "next_question": "<one sentence question, or null if should_end is true>",
  "should_end": <true or false>
}}

VALIDATION CHECKLIST before returning:
□ score_adjusted is integer between 1 and 10
□ approved_topic_id exists in the topics list above
□ If should_end is true → next_question must be null
□ If should_end is false → next_question must not be null
□ next_question is ONE sentence maximum
□ next_question does NOT start with forbidden openers listed above
□ Response is valid JSON with no trailing commas"""

    response_text = call_llm(prompt, retries=3)

    if not response_text:
        return _critic_fallback(eval_result, plan, coverage)

    result = extract_json(response_text)
    if not result:
        return _critic_fallback(eval_result, plan, coverage)

    # ── Hard validations ──────────────────────────────────────
    # Score bounds
    try:
        result["score_adjusted"] = max(1, min(10, int(result["score_adjusted"])))
    except (ValueError, TypeError):
        result["score_adjusted"] = eval_result.get("score", 5)

    # Hard cap — force end if over limit
    if turn_count >= hard_cap:
        result["should_end"] = True

    # Enforce: if ending, no question
    if result.get("should_end"):
        result["next_question"] = None

    # Enforce: if not ending, must have a question
    if not result.get("should_end") and not result.get("next_question"):
        result["next_question"] = _fallback_question(plan, coverage)

    # Validate topic id exists in plan
    valid_ids = {t["id"] for t in plan.get("topics", [])}
    if result.get("approved_topic_id") not in valid_ids:
        # Pick next uncovered topic
        covered = set(coverage.get("covered_ids", []))
        weak = set(coverage.get("weak_ids", []))
        for t in sorted(plan.get("topics", []), key=lambda x: x["priority"]):
            if t["id"] not in covered:
                result["approved_topic_id"] = t["id"]
                break

    return result


def _fallback_question(plan: dict, coverage: dict) -> str:
    """Generate a sensible fallback question based on uncovered topics."""
    covered = set(coverage.get("covered_ids", []))
    weak = set(coverage.get("weak_ids", []))

    for topic in sorted(plan.get("topics", []), key=lambda x: x["priority"]):
        if topic["id"] not in covered:
            topic_name = topic.get("topic", "your recent work")
            return f"Walk me through how you've worked with {topic_name} in your projects."

    return "What's a technical decision you made recently that you'd do differently now?"


def _critic_fallback(eval_result: dict, plan: dict, coverage: dict) -> dict:
    """Full fallback when LLM call fails entirely."""
    covered = set(coverage.get("covered_ids", []))
    next_topic_id = None

    for topic in sorted(plan.get("topics", []), key=lambda x: x["priority"]):
        if topic["id"] not in covered:
            next_topic_id = topic["id"]
            break

    return {
        "score_adjusted": eval_result.get("score", 5),
        "score_change_reason": None,
        "approved_topic_id": next_topic_id or eval_result.get("proposed_next_topic_id"),
        "override_reason": None,
        "next_question": _fallback_question(plan, coverage),
        "should_end": False
    }