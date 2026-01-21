import streamlit as st

st.set_page_config(page_title="SVCE Entrance Exam", layout="wide")

st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1">
""", unsafe_allow_html=True)

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Login", "Take Exam", "Results", "Admin", "Rank List"])

if selection == "Login":
    import pages.Login as page
    page.app()

if selection == "Take Exam":
    import pages.Take_Exam as page
    page.app()

if selection == "Results":
    import pages.Results as page
    page.app()

if selection == "Admin":
    import pages.Admin as page
    page.app()

if selection == "Rank List":
    import pages.Ranklist as page
    page.app()
