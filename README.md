# AI Summary App

AI-powered article summarization application.

## Tech Stack

Backend
- FastAPI
- Python

Frontend
- Flutter

AI
- Azure OpenAI API

## Architecture

Flutter App
      ↓
FastAPI
      ↓
LLM API

## API Example

POST /summarize

Request

{
 "text": "Large language models are transforming AI."
}

Response

{
 "summary": "LLMs are transforming artificial intelligence."
}

## Run Locally

Backend

cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

Mobile

cd mobile/ai_summary_app
flutter run