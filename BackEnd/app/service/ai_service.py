from google import genai
import os
from dotenv import load_dotenv

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

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    return response.text.strip()


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

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    return response.text.strip()