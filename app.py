import streamlit as st

st.set_page_config(page_title="SVCE Entrance Exam", layout="wide")

st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1">
""", unsafe_allow_html=True)

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Login", "Take Exam", "Results", "Admin", "Rank List"])

if selection == "Login":
    import pages.01_Login as page
    page.app()

if selection == "Take Exam":
    import pages.02_Take_Exam as page
    page.app()

if selection == "Results":
    import pages.03_Results as page
    page.app()

if selection == "Admin":
    import pages.04_Admin as page
    page.app()

if selection == "Rank List":
    import pages.05_Ranklist as page
    page.app()
