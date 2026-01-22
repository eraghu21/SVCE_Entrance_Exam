import streamlit as st
from sheets import open_sheet
from utils import check_password

SHEET_ID = st.secrets["sheet_id"]

def app():
    st.header("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        spreadsheet = open_sheet(SHEET_ID)
        # DEBUG (KEEP FOR NOW)
    st.write("Spreadsheet type:", type(spreadsheet))

    users_ws = spreadsheet.worksheet("Users")

    st.write("Users sheet loaded successfully")
        

        users = users_ws.get_all_records()
        user = next((u for u in users if u["Email"] == email), None)

        if not user:
            st.error("Email not registered")
            return

        if user["Attempted"] == "YES":
            st.warning("You have already submitted your exam. Scores are confidential.")
            st.session_state["user"] = user
            return

        if check_password(password, user["PasswordHash"]):
            st.session_state["user"] = user
            st.success(f"Welcome {user['Name']}!")
        else:
            st.error("Invalid password")
