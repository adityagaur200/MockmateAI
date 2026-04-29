import asyncio

from google import genai
import time
import os
from dotenv import load_dotenv
from google.genai.errors import ServerError

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_first_question(resume, jd, plan=None, retries=3):
    candidate_name = "the candidate"
    opening_angle = ""
    first_topic = ""
    first_topic_why = ""
    first_topic_depth = ""
    role = ""

    if plan:
        candidate_name = plan.get("candidate_name", "the candidate")
        opening_angle = plan.get("opening_angle", "")
        role = plan.get("role", "")
        topics = plan.get("topics", [])
        if topics:
            first_topic = topics[0].get("topic", "")
            first_topic_why = topics[0].get("why", "")
            first_topic_depth = topics[0].get("depth", "medium")

    # Depth instruction mapping
    depth_instruction = {
        "light": "Keep it broad and easy — just warm them up on this topic.",
        "medium": "Ask something that requires a real answer, not just a yes/no.",
        "deep": "Dig into specifics — they claimed expertise here, verify it."
    }.get(first_topic_depth, "Ask a focused, direct question.")

    prompt = f"""You are a senior engineer interviewing a candidate for a {role} role.
You are sharp, direct, and conversational — like a real tech lead, not a chatbot.

## CANDIDATE CONTEXT
Name: {candidate_name}
First topic to probe: {first_topic}
Why this topic matters: {first_topic_why}
Depth required: {first_topic_depth} → {depth_instruction}

## RESUME HIGHLIGHTS (use for personalization, do not repeat verbatim)
{resume[:800]}

## YOUR TASK
Ask the opening question. One sentence. Make it feel like the start of a 
real technical conversation — natural, confident, specific.

## QUESTION STYLE RULES (violating any = fail)

✅ DO:
- Ask exactly ONE question in ONE sentence
- Make it specific to something real in their resume
- Use casual, direct language like you're actually talking to them
- Start with action words: "Walk me through...", "Tell me about...", 
  "How did you...", "What was...", "Why did you...", "What's your take on..."
- If depth is "deep" → ask something that separates people who did it 
  from people who just listed it on their resume

❌ NEVER DO:
- Start with "Given your background..."
- Start with "Your profile/resume mentions..."
- Start with "Based on your experience..."
- Start with "Could you elaborate..."
- Start with "Could you walk me through..."
- Put any context before the question (NO setup sentences)
- Ask two things in one question (NO "and also", NO "additionally")
- Use corporate interview language ("leverage", "utilize", "elaborate on")
- Write more than one sentence

## CALIBRATED EXAMPLES BY DEPTH

LIGHT (warm-up):
✅ "What's a project you've built recently that you're actually proud of?"
✅ "Tell me about the most interesting technical challenge you've faced this year."
✅ "What kind of work do you find most energizing as an engineer?"

MEDIUM (real answer required):
✅ "How did you approach the WebSocket architecture in SynQ?"
✅ "What made you choose Spring Boot over other frameworks for LinkXpert?"
✅ "Walk me through how you handle database migrations across your projects."
✅ "What's your strategy for API error handling in a microservices setup?"

DEEP (claim verification):
✅ "When your WebSocket connections drop under load in SynQ, how do you recover state?"
✅ "How do you prevent N+1 queries in your Spring Boot services — what's your actual approach?"
✅ "If a pod in your LinkXpert cluster goes down mid-request, what happens to the user?"
✅ "How do you debug a memory leak in a Java service that's been running for weeks?"

## BAD EXAMPLES — NEVER produce these:
❌ "Your SynQ project highlights real-time messaging. Could you walk me through 
   the architectural choices and implementation details that enabled sub-200ms latency?"
❌ "Given your background with Spring Boot across multiple projects, describe a 
   scenario where you optimized a critical API endpoint."
❌ "Your profile mentions hands-on experience with AWS and Docker. Could you walk 
   me through a CI/CD pipeline you implemented?"

## OUTPUT
Return the question ONLY. No quotes around it. No explanation. No punctuation at the end other than "?".
One line. That's it."""

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            question = response.text.strip()
            # Strip quotes if model wraps in them
            question = question.strip('"').strip("'")
            return question

        except ServerError as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                print("❌ All retries failed")

    # Fallback — natural sounding, not generic
    return f"Walk me through a project you've built that you're genuinely proud of."