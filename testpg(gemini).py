import streamlit as st
## gemini idk seesion stae but it works
def pg1():
    st.title("Milestone 1")

    def next_page():
        if st.button("Next Lesson"):
            st.session_state.current_page = "pg2"  # Update session state

    next_page()

def pg2():
    st.title("Milestone 2")

    def next_page():
        if st.button("Next Lesson"):
            st.session_state.current_page = "pg3"

    next_page()

def pg3():
    st.title("Milestone 3")

    def next_page():
        if st.button("Next Lesson"):
            st.session_state.current_page = "pg4"

    next_page()

def pg4():
    st.title("Milestone 4")

def main():
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "pg1"

    # Render the appropriate page based on session state
    if st.session_state.current_page == "pg1":
        pg1()
    elif st.session_state.current_page == "pg2":
        pg2()
    elif st.session_state.current_page == "pg3":
        pg3()
    elif st.session_state.current_page == "pg4":
        pg4()

if __name__ == "__main__":
    main()