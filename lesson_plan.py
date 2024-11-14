import streamlit as st
import json
import os
import time
from whapi import search, return_details
import wikihowunofficialapi as wha
from openai import OpenAI


client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) 

st.title("Plan your lesson 101")

goal = st.text_input("Type your goal that you want to achieve")

url = ""

def get_wikihow():
    global article_id
    global url
    global article
    st.write("Searching for WikiHow article...")
    while True:
        search_result = search(goal, 1)
        article_id = search_result[0]["article_id"]
        article_info = return_details(article_id)
        if not article_info.get("low_quality", False) and not article_info.get("is_stub", False):
            url = article_info["url"]
            article = wha.Article(url)
            break
    article_dict = {
        "title": article.title,
        "intro": article.intro,
        "methods": [
            {
                "method": method.title,
                "steps": [
                    {
                        "step": step.title,
                        "description": step.description,
                    }
                    for step in method.steps
                ]
            }
            for method in article.methods
        ]
    }
    return json.dumps(article_dict, indent=4)

def generate_plan():
    article_json = get_wikihow()
    st.write("Generating plan...")
    plan_response= client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """ 
            You are a teacher who wants to create a lesson plan for a hobby.
            You are given a related WikiHow article on the hobby as a JSON string.
            The lesson plan should be based on this article.
            The lesson plan must be structured around milestones to help people learn new hobbies.
            Do not include any information that is not in the article.
            Do not include instructions to buy any additional materials, items, equipment or tools, even if they are mentioned in the article.
            You can make suggestions for commonly available items, but the lesson plan should not depend on them.
            Use decimal format for any non-integer quantities. 
            Only output raw JSON without any additional formatting or text.
            The JSON output should follow the schema below:
            {
                "hobby": "",
                "description": "",
                "prerequisites": "",
                "milestones": [
                    {
                    "title": "",
                    "description": "",
                    "objectives": [
                        {
                        "title": "",
                        "description": "",
                        },
                    ]
                    },
                ]
                }
            """},
            {"role": "user", "content": article_json}
        ]
    )
    #st.write(plan_response.choices[0].message.content)
    return json.loads(plan_response.choices[0].message.content)

def print_plan():
    lesson_plan = generate_plan()

    st.markdown(f"# {lesson_plan['hobby']}")
    st.divider()
    st.markdown("## Prerequisites")
    st.write(lesson_plan['prerequisites'])
    st.divider()
    st.markdown("## Milestones")
    for milestone in lesson_plan['milestones']:
        st.markdown(f"### {milestone['title']}")
        st.write(milestone['description'])
        st.markdown("#### Objectives")
        #with st.expander("Objectives"):
        for objective in milestone['objectives']:
            #st.write(f"##### {objective['title']}")
            #TODO: Page reloads when checkbox is clicked
            st.checkbox(objective['title'])
            st.write(objective['description'])
            st.divider()
        #st.divider()
    st.caption("More details can be found in: " + url)

if st.button("Generate Plan"):
    if goal == "":
        st.write("What? You have no goals in life?")
        time.sleep(4)
        st.rerun()
    else:
        #get_wikihow()
        #generate_plan()
        print_plan()
        st.balloons()