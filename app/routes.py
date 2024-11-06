from flask import Blueprint, request, jsonify
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from app.config import Config
from app.utils import GENERAL_PROMPT_TEMPLATE, EXTRACTED_TEXT_PROMPT_TEMPLATE
import os


api_bp = Blueprint('api', __name__)

# Configure Google API
GOOGLE_API_KEY=os.getenv('api_key')
genai.configure(api_key=GOOGLE_API_KEY)
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)

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