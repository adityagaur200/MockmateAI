from google import genai
import time
import os
from dotenv import load_dotenv
from google.genai.errors import ServerError

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def generate_first_question(resume, jd):
    prompt = f"""
    You are an AI interviewer.

    Resume:
    {resume}

    Job Description:
    {jd}

    Ask the first interview question.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except ServerError as e:
        print(f"❌ Error in generate_first_question: {e}")
        return "Sorry, I'm having trouble generating a question right now."


async def generate_next_question(resume, jd, history):
    prompt = f"""
    You are a smart AI interviewer.

    Resume:
    {resume}

    Job Description:
    {jd}

    Previous Interview History:
    {history}

    Rules:
    - Ask only ONE next question
    - If answer was weak → ask follow-up
    - If strong → move to new topic
    - Avoid repetition
   

    Return only the question.
    """

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            return response.text.strip()

        except ServerError:
            print(f"⚠️ Retry next_question {attempt+1}")
            time.sleep(2 * (attempt + 1))

    # 🔥 fallback
    return "Can you explain your recent project in detail?"
    print("❌ Gemini error in generate_next_question")
    