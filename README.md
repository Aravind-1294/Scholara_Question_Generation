# ⚙️ Question Generation Backend (Scholara)

## 📌 Overview
This repository contains the **backend service** for the Scholara AI system — an application designed to generate context-aware questions from user-provided text using Large Language Models (LLMs).

The backend is responsible for handling input processing, interacting with LLMs, and serving generated questions via API endpoints.

---

## 🎯 Problem Statement
Students often struggle to create meaningful practice questions from their study material. This backend system automates the process by generating relevant and context-aware questions using AI.

---

## 🧠 System Architecture

User Input → Backend API → LLM Processing → Generated Questions → Response

---

## 🛠️ Tech Stack

- Python  
- FastAPI / Flask *(update based on your implementation)*  
- LLM APIs (OpenAI / HuggingFace)  
- LangChain *(if used)*  
- JSON-based API communication  

---

## ⚙️ Features

- REST API for question generation  
- Context-aware question generation using LLMs  
- Prompt engineering for improved output quality  
- Modular backend architecture  
- Scalable design for integration with frontend systems  

---

## 📂 Project Structure


question_generation/
├── app/
│ ├── routes/
│ ├── services/
│ ├── utils/
├── main.py
├── requirements.txt
├── README.md


---

🔌 API Usage
Example Endpoint:
POST /generate-questions
Request Body:
{
  "text": "Input study material or notes here"
}
Response:
{
  "questions": [
    "Generated question 1",
    "Generated question 2"
  ]
}
🔗 Integration

This backend is part of the Scholara AI system:

##👉 Frontend Repo:
https://github.com/Aravind-1294/Scholara
 (update if needed)

##📊 Functionality
Accepts input text via API
Processes content using LLMs
Applies prompt engineering
Returns structured question outputs

##🚀 Future Improvements
Add caching for faster responses (Redis)
Implement evaluation metrics for question quality
Add user authentication
Deploy backend using Docker + AWS
Add streaming responses

##🧠 Key Learnings
Building backend systems for AI applications
Integrating LLMs into APIs
Designing scalable AI services
Structuring modular backend architecture

## ▶️ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Aravind-1294/question_generation.git
cd question_generation
2. Install dependencies
pip install -r requirements.txt
3. Run the backend server
python main.py

(If using FastAPI, you can use:)

uvicorn main:app --reload
