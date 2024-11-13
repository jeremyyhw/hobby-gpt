import streamlit as st
import wikipi
import os
from whapi import get_id
from whapi import random_article
from whapi import return_details
from dotenv import load_dotenv
from openai import OpenAI
from whapi import search
from whapi import return_details


client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY')) 

st.title("Plan your lesson 101")

goal = st.text_input("Type your goal that you want to achieve")
if st.button("Generate"):
    def generate_goal():

        search_results = search(goal, 1)

        URL = search_results[0:2][0]['url']

        response_hobby= client.chat.completions.create(
            model="gpt-4o-mini",

            messages=[
                
                {"role": "system", "content": """ 
                You are given the task to design a lesson plan for the user based on""" 
                + goal +
                """
                The output should be in json without any additionally formatting and describe the tasks.
                    {
                        "Prerequisite": str
                        "Month Number":int
                        "Week number":{
                            "Task number": str
                            "Task number": str
                            }
                        "Month Number":int
                        "Week number":{
                            "Task number": str
                            "Task number": str
                            }
                        "Month Number":int
                        "Week number":{
                            "Task number": str
                            "Task number": str
                            }
                    }
                The month number, week number and tasks can be more than two.
                """},
                {"role": "user", "content": "Please summarize and give a training plan based on " + URL},
            ]
        
        )
        return st.write(response_hobby.choices[0].message.content)
    generate_goal()
else:
    st.balloons()
