import streamlit as st

def app():
    if "user" not in st.session_state:
        st.error("Login first")
        return

    st.header("Exam Status")
    st.info("Your exam has been submitted successfully.\nScores are confidential and will be available to the admin only.")
