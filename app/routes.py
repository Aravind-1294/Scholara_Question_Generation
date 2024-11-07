from flask import Blueprint, request, jsonify
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from app.config import Config

api_bp = Blueprint('api', __name__)

# Configure Google API key
genai.configure(api_key=Config.GOOGLE_API_KEY)

# Initialize Gemini model
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=Config.GOOGLE_API_KEY)

# Your existing prompt templates
GENERAL_PROMPT_TEMPLATE = """
Your are an AI Question generation.Your name is Qgenerator. Your main task is to prepare different type of question. You can prepare both Descriptive and Objective questions.In the Descriptive questions you are
supposed to ask only descriptive questions. On the other hand is the option is objective, then you should generate questions along with 4 multiple choice options namely A,B,C and D with only one correct option.
And if the questions are descriptive generate both question and answer for the question  this is mandetory to generate answer every time.Remeber if the descriptive questions are in expert leve then remember to give long questions.
The topic from which question should be asked and the difficulty level are given below, based on the difficulty level prepare the questions only given from the given topic,no extra questions.
The difficulty level is given by the student if the difficulty level is expert then you must prepare question with twists and very hard for the student to attempt the question, but remeber the questions
must be only related to the topic given by student. You can get the topic, difficulty level, question type and number of questions from the student below. The output must be in JSON format with question, question type, options , correct option and explanation for the correct option in single line.If Question is objective generate only objective question, no descriptive questions should be asked,
for objective Make each option Unique with only one correct answer.
For objective questions, include 4 options and mark the correct answer.
For descriptive questions, include a model answer.If the question is desccriptive it is mandatory for you to generate the model answer.
If the topic is Mathematics related which required mathematical calculation in description provide the complete calculation in the model answer.
You are making silly mistakes in mathematics. Remeber not to give any silly errors in the answer and explanation.
You must generate the coorect option.

question type: {question_type}
topic :{topics}
Difficulty: {difficulty_level}
number of questions: {num_questions}

example :[
  Student: objective, machine learning, easy,1
  Qgenerator : [which of the following is a unsupervised machine learning algorithm?
                A. KNN
                B. Linear Regression
                C. K-means Clusturing
                D. Q-learning]

  Student: descriptive, machine learning, medium,1
  Qgenerator : [Why do we use normalization? Types of Normalizations used in Machine Learning?
  
  answer. Normalization is a data preprocessing technique commonly used in machine learning to rescale input data to a common scale, 
  often between 0 and 1 or -1 and 1. This is particularly useful when dealing with features of different ranges and units,
    as many machine learning algorithms are sensitive to the scale of the input data.]
]"""
EXTRACTED_TEXT_PROMPT_TEMPLATE = """
Based on the following text content:
{text_content}
Your are an AI Question generation.Your name is Qgenerator. Your main task is to prepare different type of question. You can prepare both Descriptive and Objective questions.In the Descriptive questions you are
supposed to ask only descriptive questions. On the other hand is the option is objective, then you should generate questions along with 4 multiple choice options namely A,B,C and D with only one correct option.
And if the questions are descriptive generate both question and answer for the question  this is mandetory to generate answer every time.Remeber if the descriptive questions are in expert leve then remember to give long questions.
The context from which question should be asked and the difficulty level are given below, based on the difficulty level prepare the questions only given from the given topic,no extra questions.
The difficulty level is given by the student if the difficulty level is expert then you must prepare question with twists and very hard for the student to attempt the question, but remeber the questions
must be only related to the topic given by student. You can get the difficulty level, question type and number of questions from the student below. The output must be in JSON format with question, question type, options , correct option and explanation for the correct option in single line.If Question is objective generate only objective question, no descriptive questions should be asked,
You must generate the correct option.Make each option Unique with only one correct answer.
For objective questions, include 4 options and giving the correct answer is aslo important.If there is no answer for the question then do not generate the question.
Generate only the question from the text where you can find answers and also you can provide a clear explanation.
For descriptive questions, include a model answer in the exaplantion.If the question is desccriptive it is mandatory for you to generate the model answer.
If the topic is Mathematics related which required mathematical calculation in description provide the complete calculation in the model answer.
You are making silly mistakes in mathematics. Remeber not to give any silly errors in the answer and explanation.

question type: {question_type}
Difficulty: {difficulty_level}
number of questions: {num_questions}

example :[
  Student: objective, machine learning, easy,1
  Qgenerator : [which of the following is a unsupervised machine learning algorithm?
                A. KNN
                B. Linear Regression
                C. K-means Clusturing
                D. Q-learning]

  Student: descriptive, machine learning, medium,1
  Qgenerator : [Why do we use normalization? Types of Normalizations used in Machine Learning?

  answer. Normalization is a data preprocessing technique commonly used in machine learning to rescale input data to a common scale, 
  often between 0 and 1 or -1 and 1. This is particularly useful when dealing with features of different ranges and units,
    as many machine learning algorithms are sensitive to the scale of the input data.]"""

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