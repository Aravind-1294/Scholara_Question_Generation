from flask import Flask,jsonify
import pathlib
import textwrap
import json
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from langchain import Cohere, ConversationChain, LLMChain, PromptTemplate
from langchain.chains import SimpleSequentialChain, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv


app=Flask(__name__)
load_dotenv()
super = ChatGoogleGenerativeAI(model='gemini-pro',google_api_key=os.getenv('api_key'))

prompt ="""Your are an AI Question generation.Your name is Qgenerator. Your main task is to prepare different type of question. You can prepare both Descriptive and Objective questions.In the Descriptive questions you are 
supposed to ask only descriptive questions. On the other hand is the option is objective, then you should generate questions along with 4 multiple choice options namely A,B,C and D with only one correct option
The Topic and the difficulty level are given below, based on the difficulty level prepare the questions only related to relevent topic,no extra questions rather than topic. 
The difficulty level is given by the student if the difficulty level is expert then you must prepare question with twists and very hard for the student to attempt the question, but remeber the questions 
must be only related to the topic given by student. You can get the topic, difficulty level, question type and number of questions from the student below. The output must be in JSON format with question, question type, options , correct option and explanation for the correct option in single line.If Question is objective generate only objective question, no descriptive questions should be asked.
question type: {question}
topic :{topic}
Difficulty: {difficulty}
number of questions: {number}

example :[
  Student: objective, machine learning, easy,1
  Qgenerator : [which of the following is a unsupervised machine learning algorithm?
                A. KNN
                B. Linear Regressions
                C. K-means Clusturing
                D. Q-learning] 

  Student: descriptive, machine learning, medium,1
  Qgenerator : [Why do we use normalization? Types of Normalizations used in Machine Learning?]
]

"""

template = prompt
promptTemplate = PromptTemplate(input_variables=["question","topic","difficulty","number"], template=template)
synopsisChain = LLMChain(
    llm=super,
    prompt=promptTemplate,
    verbose=True,
)


@app.route('/get/<question_type>/<topic>/<difficulty>/<number>')
def welcome(question_type, topic, difficulty, number):
    try:
        all_questions = []
        number = int(number)
        
        if number > 10:

            for i in range(0, number, 10):
        
                output = synopsisChain.run(
                    question=question_type,
                    topic=topic,
                    difficulty=difficulty,
                    number=min(10, number - i)  
                )
                
                
                if isinstance(output, str):
                    output = json.loads(output)
                
            
                if isinstance(output, list):
                    all_questions.extend(output)
                else:
                    all_questions.append(output)
                
        else:
            
            output = synopsisChain.run(
                question=question_type,
                topic=topic,
                difficulty=difficulty,
                number=number
            )
            
            
            if isinstance(output, str):
                output = json.loads(output)
            
            
            if isinstance(output, list):
                all_questions.extend(output)
            else:
                all_questions.append(output)
        

        return jsonify({
            "status": "success",
            "questions": all_questions,
            "count": len(all_questions)
        })
        
    except json.JSONDecodeError as e:
        return jsonify({
            "status": "error",
            "message": f"Invalid JSON format: {str(e)}",
            "questions": []
        }), 400
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "questions": []
        }), 500
if __name__=='__main__':
    app.run()