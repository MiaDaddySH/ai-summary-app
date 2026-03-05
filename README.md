![Flutter](https://img.shields.io/badge/Flutter-Mobile-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-purple)

# AI Summary App

An AI-powered mobile application that summarizes web articles using Large Language Models.

Users can paste any article URL or text and receive concise summaries in both English and Chinese.

---

## Demo Screenshot

<p align="center">
  <img src="screenshots/iphone1.png" width="30%" style="margin-right:10px;"/>
  <img src="screenshots/iphone2.png" width="30%" style="margin-right:10px;"/>
  <img src="screenshots/iphone3.png" width="30%"/>
</p>

---

## Features

- Summarize articles from URL
- Extract main content from webpages
- Generate summaries using AI
- English + Chinese summaries
- Mobile UI built with Flutter
- Backend API built with FastAPI
- Azure OpenAI integration

---

## Tech Stack

Frontend
- Flutter

Backend
- FastAPI
- Python

AI
- Azure OpenAI

Web Content Extraction
- Readability
- BeautifulSoup

---

## Architecture

```mermaid
flowchart TD
  A[Flutter Mobile App] -->|POST /summarize| B[FastAPI Backend]
  B --> C[Article Fetcher<br/>httpx + readability + bs4]
  C --> D[Azure OpenAI<br/>OpenAI-compatible endpoint]
  D --> B
  B -->|summary| A
```

---

## How to Run

### Backend

```
cd backend
uvicorn app.main:app --reload
```

### Mobile
```
cd mobile/ai_summary_app
flutter run
```


---

## Future Improvements

- History of summarized articles
- Share summaries
- Support PDF summarization
- Support more languages

