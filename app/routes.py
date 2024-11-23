from flask import Blueprint, request, jsonify
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from app.config import Config

api_bp = Blueprint('api', __name__)

# Configure Google API key
genai.configure(api_key=Config.GOOGLE_API_KEY)

# Initialize Gemini model
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=Config.GOOGLE_API_KEY)

# Updated prompt templates for MCQs only
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
  Student: mcq, machine learning, easy, 1
  Qgenerator: [which of the following is a unsupervised machine learning algorithm?
                A. KNN
                B. Linear Regression
                C. K-means Clustering
                D. Q-learning]
]"""

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
  Student: mcq, machine learning, easy, 1
  Qgenerator: [which of the following is a unsupervised machine learning algorithm?
                A. KNN
                B. Linear Regression
                C. K-means Clustering
                D. Q-learning]
]"""

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
