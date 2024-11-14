import streamlit as st
import json
import os
import time
from whapi import search, return_details
import wikihowunofficialapi as wha
from openai import OpenAI

st.set_page_config(
    page_title= "How to Basic",
    page_icon= "nerd_face"
)


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
            
            if 'url' not in st.session_state:
                st.session_state.url = article_info["url"]
            url = st.session_state.url

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
            Do not use the words "buy", "purchase", or "invest in" in the lesson plan.
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
    if 'lesson_plan' not in st.session_state:
        st.session_state['lesson_plan'] = generate_plan()
    lesson_plan = st.session_state.lesson_plan

    st.markdown(f"# {lesson_plan['hobby']}")
    st.caption("More details can be found in: " + st.session_state.url)
    st.divider()
    st.markdown("## Prerequisites")
    st.write(lesson_plan['prerequisites'])
    st.divider()
    st.markdown("## Milestones")

    for i, milestone in enumerate(lesson_plan['milestones']):
        if f'milestone_{i}_completed' not in st.session_state:
            st.session_state[f'milestone_{i}_completed'] = False

        form_key = f"milestone_form_{i}"
        with st.form(key=form_key):
            st.markdown(f"### {milestone['title']}")
            st.write(milestone['description'])

            st.markdown("#### Objectives")
            for objective in milestone['objectives']:
                st.checkbox(objective['title'], key=f"objective_{objective['title']}")
                st.write(objective['description'])

            #TODO: bugfix - Have to click the button twice to mark as completed
            if st.session_state[f'milestone_{i}_completed'] == True:
                completed = st.form_submit_button("Milestone Complete", type="primary", disabled=True, use_container_width=True)
                st.subheader(f"Congratulations on completing Milestone {i+1}: {milestone['title']}!")
            else:
                completed = st.form_submit_button("Complete Milestone", type="primary", use_container_width=True)
                if completed:
                    st.session_state[f'milestone_{i}_completed'] = True
                    

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

if st.session_state.clicked is False:
    if st.button("Generate Plan"):
        if goal == "":
            st.write("What? You have no goals in life?")
            time.sleep(4)
            st.rerun()
        else:
            st.session_state.clicked = True 
            print_plan()
            st.balloons()

if st.session_state.clicked is True:
    print_plan()