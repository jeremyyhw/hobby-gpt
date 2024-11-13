import streamlit as st

def pg4():
    st.title("Milestone 4")
    def nextpg():
        if st.button("Next Lesson"):
            pag1 = st.navigation([st.Page(pg4), st.Page(pg1)])
            pag1.run(pg1)
            pg1()
    nextpg()
    
def pg3():
    st.title("Milestone 3")
    def nextpg():
        if st.button("Next Lesson"):
            pag4 = st.navigation([st.Page(pg3), st.Page(pg4)])
            pag4.run(pg4)
            pg3()
    nextpg()

def pg2():
    st.title("Milestone 2")
    def nextpg():
        if st.button("Next Lesson"):
            pag3 = st.navigation([st.Page(pg2), st.Page(pg3)])
            pag3.run()
            pg2()
    nextpg()

def pg1():
    st.title("Milestone 1")
    def nextpg():
        if st.button("Next Lesson"):
            pag2 = st.navigation([st.Page("streamlit_wikipi.py"), st.Page(pg2)])
            pag2.run(pg2)
    nextpg()
pg1()

