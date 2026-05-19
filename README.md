# 🚀 MockMate AI

An AI-powered mock interview platform that simulates real interview experiences using adaptive questioning, resume analysis, speech-to-text processing, and intelligent AI evaluation.

MockMate AI dynamically generates interview questions based on the candidate’s resume, job description (JD), and previous answers. The platform leverages Generative AI, RAG architecture, Whisper speech-to-text, Redis, Celery, and LangChain to deliver personalized interview experiences with real-time feedback and scoring.

---

# ✨ Features

## 🧠 AI-Powered Interview Engine
- Dynamic interview question generation using Gemini API
- Questions generated based on:
  - Resume
  - Job Description (JD)
  - Candidate responses
- Adaptive questioning strategy
- Context-aware follow-up questions

---

## 📄 Resume Analysis
- AI-powered resume parsing and analysis
- Skill extraction from resumes
- Experience and project understanding
- Resume-to-JD matching

---

## 🎤 Speech-to-Text Support
- Voice answer support using Whisper Model
- Converts spoken responses into text
- Enables realistic interview simulations

---

## 🔍 RAG (Retrieval-Augmented Generation)
- Uses LangChain-based RAG pipeline
- Retrieves relevant resume/JD context before question generation
- Improves contextual accuracy of AI responses

---

## 📊 AI Evaluation & Scoring
- LLM-based answer evaluation
- Communication scoring
- Technical accuracy scoring
- Confidence and relevance analysis
- Final AI-generated interview feedback report

---

## ⚡ Background Processing
- Redis for caching and task queue management
- Celery for asynchronous AI task execution
- Efficient handling of long-running AI operations

---

# 🛠️ Tech Stack

## Frontend
- React.js
- Tailwind CSS
- Axios

## Backend
- FastAPI
- Python

## Database
- MongoDB

## AI & ML
- Gemini API
- LangChain
- Whisper Model
- RAG Architecture

## Authentication
- JWT Authentication

## DevOps & Infrastructure
- Docker
- Redis
- Celery

---

# 🏗️ System Architecture

```mermaid
flowchart TD

A[User] --> B[React Frontend]

B --> C[FastAPI Backend]

C --> D[JWT Authentication]

C --> E[Resume Upload]
C --> F[Job Description Upload]
C --> G[Voice Answer Upload]

G --> H[Whisper Speech-to-Text]

E --> I[Resume Analyzer]
F --> I

I --> J[LangChain RAG Pipeline]

J --> K[Gemini API]

K --> L[Interview Planning Engine]

L --> M[Dynamic Question Generator]

M --> N[Adaptive Follow-up Questions]

N --> O[LLM Evaluation Engine]

O --> P[AI Scoring & Feedback]

C --> Q[(MongoDB)]

C --> R[(Redis Queue)]

R --> S[Celery Workers]

S --> K
