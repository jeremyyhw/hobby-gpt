
import os
from whapi import get_id
from whapi import random_article
from whapi import return_details
from dotenv import load_dotenv
from openai import OpenAI
from whapi import search
from whapi import return_details


load_dotenv()

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY')) 




x = input("Tell me your goal that you want to achieve: ")

search_results = search(x, 1)
#article_info = return_details(search_results[0:3])

URL = search_results[0:2][0]['url']

response_hobby= client.chat.completions.create(
    model="gpt-4o-mini",

    messages=[
        
        {"role": "system", "content": """ 
         You are given the task to design a lesson plan for the user based on""" 
         + x +
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
        The task can be more than two.
        """},
        {"role": "user", "content": "Please summarize and give a training plan based on " + URL},
    ]
)

print(URL)
print(response_hobby.choices[0].message.content)
