import streamlit as st
import json
import time
from whapi import search, return_details
import wikihowunofficialapi as wha
from openai import OpenAI

st.set_page_config(
    page_title= "HowTo.Basic",
    page_icon= "nerd_face"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) 

st.markdown("""<h1 style='text-align: center; color: white;'>Plan your lesson with AI</h1>""", unsafe_allow_html=True)

goal = st.text_input("What do you want to learn today?")

url = ""

def get_wikihow():
    global article_id
    global url
    global article

    try:
        while True:
            # use whapi to search wikihow with the goal input as search term and get first result
            search_result = search(goal, max_results=1)
            # get the article id of the first result
            article_id = search_result[0]["article_id"]
            # get the details of the article as a python dict
            article_info = return_details(article_id)
            if not article_info.get("low_quality", False) and not article_info.get("is_stub", False):
                
                if 'url' not in st.session_state:
                    st.session_state.url = article_info["url"]
                url = st.session_state.url

                article = wha.Article(url)
                break
    except Exception as e:
        st.write("An API error occurred while searching for the WikiHow article. Please try again later.")
        st.write(e)

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
    plan_response= client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """ 
            You are a multi-talented subject expert and mentor who is passionate about teaching people new skills.
            You want to create a lesson plan for a hobby. You are given a related WikiHow article on this hobby as a JSON string.
            The lesson plan should be based on this article. Do not include any information that is not in the article.
            The lesson plan must be structured around milestones to help people learn new hobbies.
            Do not include instructions to buy any additional materials, items, equipment or tools, even if they are mentioned in the article.
            Do not include instructions to purchase any services or pay for any subscriptions.
            Do not include instructions to invest money in any way. Do not use the words "buy", "purchase", or "invest in".
            You can make suggestions to use commonly available items, but the lesson plan should not depend on them.
            Use decimal format for any non-integer quantities. 
            Only output raw JSON without any additional formatting or text.
            The JSON output should follow the format below:
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
    return json.loads(plan_response.choices[0].message.content)

def modify_milestone(milestone1, feedback, milestone2):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
            {"role":"system", "content":f"""
            You are a multi-talented subject expert and mentor who is passionate about teaching people new skills.
            You are given the following milestones for a goal-based lesson plan. Milestone 1: {milestone1} Milestone 2: {milestone2}
            The user has already completed Milestone 1 and has provided feedback for it. You need to modify Milestone 2 based on this feedback.
            Do not include instructions to buy any additional materials, items, equipment or tools, even if they are mentioned in the article.
            Do not include instructions to purchase any services or pay for any subscriptions.
            Do not include instructions to invest money in any way. Do not use the words "buy", "purchase", or "invest in".
            You can make suggestions to use commonly available items, but the lesson plan should not depend on them.
            Use decimal format for any non-integer quantities. 
            Only output raw JSON without any additional formatting or text."""
            + """
            The JSON output should follow the format below:
            {
                "title": "",
                "description": "",
                "objectives": [
                    {
                    "title": "",
                    "description": "",
                    },
                ]
            }
            """},
            {"role":"user", "content":feedback}
        ],
    )
    return json.loads(response.choices[0].message.content)

def display_milestone(milestone_json, index):
    milestone = json.loads(milestone_json)
    form_key = f"milestone_form_{index}"
    
    with st.form(form_key):
        st.markdown(f"### {index + 1} - {milestone['title']}")
        st.write(milestone['description'])
        
        st.markdown("#### Objectives")
        for objective in milestone['objectives']:
            st.checkbox(objective['title'], key=f"objective_{objective['title']}")
            st.write(objective['description'])

        feedback = st.text_area("You can provide feedback for this milestone. Please leave it blank if you have no feedback.", key=f"feedback_{index}")
        
        if st.session_state[f'milestone_{index}_completed']:
            st.form_submit_button("Milestone Complete", type="primary", disabled=True, use_container_width=True)
        else:
            if st.form_submit_button("Complete Milestone", type="primary", use_container_width=True):
                if feedback is not "":
                    st.session_state[f'milestone_{index}_feedback'] = feedback
                st.session_state[f'milestone_{index}_completed'] = True
                st.rerun()

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

    # Initialize all milestone states at the start
    for i in range(len(lesson_plan['milestones'])):
        if f'milestone_{i}_completed' not in st.session_state:
            st.session_state[f'milestone_{i}_completed'] = False

    # Calculate progress
    completed_milestones = sum(st.session_state[f'milestone_{i}_completed'] for i in range(len(lesson_plan['milestones'])))
    total_milestones = len(lesson_plan['milestones'])
    progress = int((completed_milestones / total_milestones) * 100)

    # Display progress bar
    st.progress(progress, text=f"{completed_milestones}/{total_milestones} Milestones Completed")
    if progress == 100:
        st.success("🎉 Congratulations! You've completed all milestones!")
        st.balloons()

    for i, milestone in enumerate(lesson_plan['milestones']):
        # Show milestone only if it's the first one or previous is completed
        should_show = i == 0 or st.session_state[f'milestone_{i-1}_completed']
        
        if should_show:
            # Modify milestone based on feedback from previous milestone
            if i > 0 and st.session_state[f'feedback_{i-1}']:
                with st.spinner(f"Modifying Milestone {i + 1} based on your feedback..."):
                    prev_milestone = json.dumps(lesson_plan['milestones'][i-1])
                    curr_milestone = json.dumps(milestone)
                    feedback = st.session_state[f'feedback_{i-1}']
                    milestone = modify_milestone(prev_milestone, curr_milestone, feedback)

            display_milestone(json.dumps(milestone), i)

            if st.session_state[f'milestone_{i}_completed']:
                st.success(f"✨ Completed Milestone {i + 1} - {milestone['title']}!")
                if st.button(label="Reset Progress", key=f"milestone_{i}_reset", use_container_width=True):
                    st.session_state[f'milestone_{i}_completed'] = False
                    if f'milestone_{i+1}_completed' in st.session_state and st.session_state[f'milestone_{i+1}_completed']:
                        st.session_state[f'milestone_{i+1}_completed'] = False
                    st.rerun()
        else:
            st.info(f"🔒 Complete previous milestone to unlock: {milestone['title']}")
    st.divider()
    st.warning('WARNING: You cannot undo the actions below, so be 100 percent sure!', icon="⚠️")
    if st.button("Reset All Progress", use_container_width=True):
        for i in range(len(lesson_plan['milestones'])):
            st.session_state[f'milestone_{i}_completed'] = False
        st.rerun()

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

if st.session_state.clicked is False:
    if st.button("Generate Plan", type="primary", use_container_width=True):
        if goal == "":
            st.write("What? You have no goals in life?")
            time.sleep(4)
            st.rerun()
        else:
            st.session_state.clicked = True
            with st.spinner("Searching for WikiHow article..."):
                time.sleep(3)
            with st.spinner("Generating plan..."):
                time.sleep(3)
            st.rerun()

if st.session_state.clicked is True:
    print_plan()
    if st.button("Generate Another Plan", type="primary", use_container_width=True):
        st.session_state.clicked = False
        st.session_state.clear()
        st.rerun()