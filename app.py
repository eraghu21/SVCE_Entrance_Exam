import streamlit as st
import pandas as pd
import random
from datetime import datetime, time

st.set_page_config("SVCE Entrance Exam", layout="wide")

# ---------------- LOAD DATA ----------------
users = pd.read_csv("users.csv")
questions = pd.read_csv("questions.csv")

# ---------------- SESSION INIT ----------------
for key in ["logged_in", "user", "exam_started", "responses", "marked"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key in ["responses", "marked"] else False

# ---------------- LOG FUNCTION ----------------
def log_event(event):
    log = pd.DataFrame([[datetime.now(), st.session_state.user["application_no"], event]],
                       columns=["time", "app_no", "event"])
    log.to_csv("logs.csv", mode="a", index=False, header=False)

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.title("🎓 SVCE Entrance Exam Portal")

    uid = st.text_input("Email / Application No")
    pwd = st.text_input("Password (DOB or Mobile)", type="password")

    if st.button("Login"):
        user = users[
            ((users.email == uid) | (users.application_no == uid)) &
            ((users.dob.astype(str) == pwd) | (users.mobile.astype(str) == pwd))
        ]

        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.user = user.iloc[0].to_dict()
            log_event("Login")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ---------------- SIDEBAR ----------------
user = st.session_state.user
st.sidebar.success(user["name"])
st.sidebar.write("App No:", user["application_no"])

if st.sidebar.button("Logout"):
    log_event("Logout")
    st.session_state.clear()
    st.experimental_rerun()

# ---------------- ADMIN PANEL ----------------
if user["role"] == "admin":
    st.title("🛠 Admin Dashboard")
    st.subheader("Results")
    try:
        st.dataframe(pd.read_csv("results.csv"))
    except:
        st.info("No results yet")
    st.subheader("Logs")
    try:
        st.dataframe(pd.read_csv("logs.csv"))
    except:
        st.info("No logs yet")
    st.stop()

# ---------------- EXAM TIME CONTROL ----------------
now = datetime.now().time()
if not (time(9,0) <= now <= time(12,0)):
    st.warning("Exam available only between 9 AM – 12 PM")
    st.stop()

# ---------------- INSTRUCTIONS ----------------
if not st.session_state.exam_started:
    st.header("📋 Instructions")
    st.markdown("""
    • Total Time: 180 minutes  
    • Minimum Submit Time: 120 minutes  
    • Auto-submit at 180 minutes  
    • Questions & options are shuffled  
    """)

    if st.checkbox("I agree"):
        if st.button("Start Exam"):
            st.session_state.exam_started = True
            st.session_state.start_time = datetime.now()
            st.session_state.qbank = questions.sample(frac=1)
            log_event("Exam Started")
            st.experimental_rerun()
    st.stop()

# ---------------- TIMER ----------------
elapsed = (datetime.now() - st.session_state.start_time).seconds
remaining = 180*60 - elapsed
st.sidebar.info(f"⏱ Time Left: {remaining//60}:{remaining%60}")

if remaining <= 0:
    st.warning("Auto submitting...")
    submit = True
else:
    submit = False

# ---------------- SECTIONS ----------------
section = st.sidebar.radio("Sections", ["Physics", "Chemistry", "Mathematics"])
qs = st.session_state.qbank[st.session_state.qbank.section == section].reset_index(drop=True)

# ---------------- QUESTION PALETTE ----------------
st.sidebar.markdown("### Question Palette")
for i in range(len(qs)):
    color = "🟢" if qs.loc[i,"qid"] in st.session_state.responses else "⚪"
    if st.sidebar.button(f"{color} Q{i+1}", key=f"qbtn{i}"):
        st.session_state.qindex = i

qindex = st.session_state.get("qindex", 0)
q = qs.iloc[qindex]

# ---------------- QUESTION DISPLAY ----------------
st.subheader(f"Q{qindex+1}. {q['question']}")

options = [q.option1, q.option2, q.option3, q.option4]
random.shuffle(options)

ans = st.radio("Options", options,
               index=options.index(st.session_state.responses[q.qid])
               if q.qid in st.session_state.responses else 0)

st.session_state.responses[q.qid] = ans

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Save & Next"):
        st.session_state.qindex = min(qindex+1, len(qs)-1)
with col2:
    if st.button("Mark for Review"):
        st.session_state.marked[q.qid] = True
with col3:
    if st.button("Clear"):
        st.session_state.responses.pop(q.qid, None)

# ---------------- SUBMIT ----------------
if (elapsed >= 120*60 and st.button("Submit Exam")) or submit:
    score = 0
    for _, row in st.session_state.qbank.iterrows():
        if st.session_state.responses.get(row.qid) == row.answer:
            score += 1

    result = pd.DataFrame([[user["name"], user["application_no"], score]],
                          columns=["Name","Application No","Score"])
    result.to_csv("results.csv", mode="a", index=False, header=False)
    log_event("Submitted")
    st.success(f"Exam Submitted! Score: {score}")
    st.stop()
