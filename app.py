import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Entrance Exam", layout="wide")

# ---------------- LOAD DATA ----------------
users = pd.read_csv("users.csv")
questions = pd.read_csv("questions.csv")

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = {}

if "responses" not in st.session_state:
    st.session_state.responses = {}

if "qindex" not in st.session_state:
    st.session_state.qindex = 0

if "current_section" not in st.session_state:
    st.session_state.current_section = "Physics"

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:
    st.title("🎓 Entrance Exam Login")

    uid = st.text_input("Email ID / Application Number")
    pwd = st.text_input("Password (DOB or Mobile)", type="password")

    if st.button("Login"):
        user = users[
            ((users["email"] == uid) | (users["application_no"] == uid)) &
            ((users["dob"].astype(str) == pwd) | (users["mobile"].astype(str) == pwd))
        ]

        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.user = user.iloc[0].to_dict()
            st.success("Login successful")
            st.experimental_rerun()
        else:
            st.error("Invalid login details")

    st.stop()

# ---------------- SIDEBAR (PROFILE) ----------------
user = st.session_state.user
st.sidebar.success(f"👤 {user['name']}")
st.sidebar.write(f"📄 Application No: {user['application_no']}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.experimental_rerun()

# ---------------- SECTION SELECTION ----------------
section = st.sidebar.radio(
    "Select Section",
    ["Physics", "Chemistry", "Mathematics"],
    index=["Physics", "Chemistry", "Mathematics"].index(st.session_state.current_section)
)

# Reset question index when section changes
if section != st.session_state.current_section:
    st.session_state.qindex = 0
    st.session_state.current_section = section

# Filter questions
section_qs = questions[questions.section == section].reset_index(drop=True)

st.title(f"📘 {section} Section")

# ---------------- QUESTION PALETTE ----------------
st.sidebar.markdown("### Question Palette")

for i in range(len(section_qs)):
    qid = section_qs.loc[i, "qid"]
    status = "🟢" if qid in st.session_state.responses else "⚪"

    if st.sidebar.button(f"{status} Q{i+1}", key=f"{section}_{i}"):
        st.session_state.qindex = i

# Safety check
if st.session_state.qindex >= len(section_qs):
    st.session_state.qindex = 0

# ---------------- QUESTION DISPLAY ----------------
q = section_qs.iloc[st.session_state.qindex]

st.subheader(f"Question {st.session_state.qindex + 1}")
st.write(q["question"])

options = [q.option1, q.option2, q.option3, q.option4]
random.shuffle(options)

selected = st.radio(
    "Choose an option:",
    options,
    index=options.index(st.session_state.responses[q.qid])
    if q.qid in st.session_state.responses else 0
)

# Save answer
st.session_state.responses[q.qid] = selected

# ---------------- NAVIGATION BUTTONS ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("Save & Next"):
        st.session_state.qindex = min(
            st.session_state.qindex + 1,
            len(section_qs) - 1
        )

with col2:
    if st.button("Clear Response"):
        st.session_state.responses.pop(q.qid, None)

# ---------------- DEBUG (OPTIONAL) ----------------
st.markdown("---")
st.subheader("🔍 Stored Answers (Testing Only)")
st.json(st.session_state.responses)
