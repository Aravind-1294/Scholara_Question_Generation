from flask import Blueprint, request, jsonify
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import Config
import tempfile
from supabase import create_client, Client
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

api_bp = Blueprint('api', __name__)

genai.configure(api_key=Config.GOOGLE_API_KEY)
supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

llm = GoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=Config.GOOGLE_API_KEY)

GENERAL_PROMPT_TEMPLATE = """
Your are an AI Question generation. Your name is Qgenerator. Your main task is to prepare Multiple Choice Questions (MCQs).
You should generate questions along with 4 multiple choice options namely A, B, C and D with only one correct option.
The topic from which question should be asked and the difficulty level are given below, based on the difficulty level prepare the questions only from the given topic, no extra questions.
The difficulty level is given by the student. If the difficulty level is expert then you must prepare questions with twists and very hard for the student to attempt, but remember the questions
must be only related to the topic given by student.

The output must be in JSON format with question, question type, options, correct option and explanation for the correct option in single line.
Make each option Unique with only one correct answer. If you have any maths or coding related questions, include the code or maths problem if you are generating such questions.
For all questions, include 4 options and mark the correct answer.
If the topic is Mathematics related which required mathematical calculation, provide the complete calculation in the explanation.
You must generate the correct option and ensure there are no silly errors in mathematics.

question type: {question_type}
topic: {topics}
Difficulty: {difficulty_level}
number of questions: {num_questions}

example:
[
  {{
    "question": "Which of the following is an unsupervised machine learning algorithm?",
    "question_type": "mcq",
    "options": [
      "KNN",
      "Linear Regression",
      "K-means Clustering",
      "Q-learning"
    ],
    "correct_option": "K-means Clustering",
    "explanation": "K-means clustering is unsupervised because it draws inferences from unlabeled data."
  }}
]
"""

EXTRACTED_TEXT_PROMPT_TEMPLATE = """
Based on the following text content:
{text_content}

Your are an AI Question generation. Your name is Qgenerator. Your main task is to prepare Multiple Choice Questions (MCQs).
You should generate questions along with 4 multiple choice options namely A, B, C and D with only one correct option.
The context from which questions should be asked and the difficulty level are given below. Based on the difficulty level, prepare the questions only from the given context, no extra questions.
The difficulty level is given by the student. If the difficulty level is expert then you must prepare questions with twists and very hard for the student to attempt, but remember the questions
must be only related to the given context.

The output must be in JSON format with question, question type, options, correct option and explanation for the correct option in single line.
Make each option Unique with only one correct answer. If you have any maths or coding related questions, include the code or maths problem if you are generating such questions.
For all questions, include 4 options and mark the correct answer.
Generate only questions where you can find answers in the text and provide clear explanations.
If the topic is Mathematics related which required mathematical calculation, provide the complete calculation in the explanation.
You must generate the correct option and ensure there are no silly errors in mathematics.

question type: {question_type}
Difficulty: {difficulty_level}
number of questions: {num_questions}

example:
[
  {{
    "question": "Which of the following is an unsupervised machine learning algorithm?",
    "question_type": "mcq",
    "options": [
      "KNN",
      "Linear Regression",
      "K-means Clustering",
      "Q-learning"
    ],
    "correct_option": "K-means Clustering",
    "explanation": "K-means clustering is unsupervised because it draws inferences from unlabeled data."
  }}
]
"""

@api_bp.route('/api/generate-general-exam', methods=['POST'])
def generate_general_exam():
    try:
        data = request.json
        
        prompt = PromptTemplate(
            template=GENERAL_PROMPT_TEMPLATE,
            input_variables=["num_questions", "question_type", "topics", "difficulty_level"]
        )
        
        formatted_prompt = prompt.format(
            num_questions=data['numQuestions'],
            question_type=data['questionType'],
            topics=data['topics'],
            difficulty_level=data['difficultyLevel']
        )
        
        response = llm.invoke(formatted_prompt)
        
        return jsonify({
            "success": True,
            "data": response
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/api/generate-extracted-text-exam', methods=['POST'])
def generate_extracted_text_exam():
    try:
        data = request.json
        
        prompt = PromptTemplate(
            template=EXTRACTED_TEXT_PROMPT_TEMPLATE,
            input_variables=["text_content", "num_questions", "question_type", "difficulty_level"]
        )
        
        formatted_prompt = prompt.format(
            text_content=data['textContent'],
            num_questions=data['numQuestions'],
            question_type=data['questionType'],
            difficulty_level=data['difficultyLevel']
        )
        
        response = llm.invoke(formatted_prompt)
        
        return jsonify({
            "success": True,
            "data": response
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/api/chat-sessions', methods=['GET'])
def get_chat_sessions():
    user_email = request.args.get('email')
    if not user_email:
        return jsonify({"success": False, "error": "Email required"}), 400
    
    try:
        response = supabase.table('exam_chat_sessions') \
            .select('*') \
            .eq('user_email', user_email) \
            .order('created_at', desc=True) \
            .execute()
        return jsonify({"success": True, "sessions": response.data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/api/embed-pdf', methods=['POST'])
def embed_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
            
        file = request.files['file']
        user_email = request.form.get('userEmail')
        pdf_name = file.filename
        session_res = supabase.table('exam_chat_sessions').insert({
            "user_email": user_email,
            "pdf_name": pdf_name
        }).execute()
        session_id = session_res.data[0]['id']
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        splits = text_splitter.split_documents(pages)
        for split in splits:
            chunk_text = split.page_content
            result = genai.embed_content(
                model="gemini-embedding-001",
                content=chunk_text,
                task_type="retrieval_document"
            )
            embedding_vector = result['embedding']
            
            supabase.table('exam_document_chunks').insert({
                "exam_id": session_id,
                "content": chunk_text,
                "embedding": embedding_vector
            }).execute()
        os.remove(tmp_path)
        return jsonify({"success": True, "sessionId": session_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



@api_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        session_id = data.get('sessionId')
        message = data.get('message')
        supabase.table('exam_chat_history').insert({
            "session_id": session_id,
            "role": "user",
            "content": message
        }).execute()
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=message,
            task_type="retrieval_query"
        )
        query_embedding = result['embedding']
        rag_response = supabase.rpc("match_exam_chunks", {
            "query_embedding": query_embedding,
            "target_exam_id": session_id,
            "match_threshold": 0.5,
            "match_count": 3
        }).execute()
        
        context_texts = [match['content'] for match in rag_response.data]
        context_block = "\n\n---\n\n".join(context_texts)
        history_response = supabase.table('exam_chat_history') \
            .select('role, content') \
            .eq('session_id', session_id) \
            .order('created_at', desc=False) \
            .limit(10) \
            .execute()
        
        history_block = ""
        for msg in history_response.data:
            role = "Student" if msg['role'] == "user" else "Tutor"
            history_block += f"{role}: {msg['content']}\n"
        chat_prompt = f"""
        You are ExamChat, an AI tutor. Answer the student's question based ONLY on the following context extracted from their uploaded PDF.
        If the answer is not in the context, say "I cannot find the answer to that in the uploaded document."
        
        PREVIOUS CHAT HISTORY:
        {history_block}
        
        PDF CONTEXT:
        {context_block}
        
        STUDENT'S NEW QUESTION:
        {message}
        """
        
        chat_response = llm.invoke(chat_prompt)
        reply_text = chat_response if isinstance(chat_response, str) else chat_response.content
        supabase.table('exam_chat_history').insert({
            "session_id": session_id,
            "role": "model",
            "content": reply_text
        }).execute()
        return jsonify({"success": True, "reply": reply_text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



@api_bp.route('/api/chat-history', methods=['GET'])
def get_chat_history():
    session_id = request.args.get('sessionId')
    if not session_id:
        return jsonify({"success": False, "error": "Session ID required"}), 400
    
    try:
        response = supabase.table('exam_chat_history') \
            .select('*') \
            .eq('session_id', session_id) \
            .order('created_at', desc=False) \
            .execute()
        return jsonify({"success": True, "messages": response.data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
