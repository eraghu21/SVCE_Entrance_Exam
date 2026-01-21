import streamlit as st
from sheets import open_sheet
import random
from datetime import datetime

SHEET_ID = st.secrets["sheet_id"]
SECTIONS = ["Physics", "Chemistry", "Maths"]

def app():
    if "user" not in st.session_state:
        st.error("Login first")
        return

    # Stop if already attempted
    if st.session_state["user"]["Attempted"] == "YES":
        st.warning("You have already submitted your exam. Scores are confidential.")
        st.stop()

    sheet = open_sheet(SHEET_ID)
    questions_all = sheet.worksheet("Questions").get_all_records()

    if "exam" not in st.session_state:
        st.session_state.exam = {}
        st.session_state.answers = {}
        st.session_state.review = set()
        st.session_state.section = SECTIONS[0]
        st.session_state.q_index = 0

        for sec in SECTIONS:
            sec_qs = [q for q in questions_all if q["Section"] == sec]
            random.shuffle(sec_qs)
            for q in sec_qs:
                opts = [q["Option A"], q["Option B"], q["Option C"], q["Option D"]]
                random.shuffle(opts)
                q["shuffled"] = opts
            st.session_state.exam[sec] = sec_qs

    st.markdown(f"### SVCE Entrance Exam - Candidate: {st.session_state['user']['Name']}")

    sec_tabs = st.tabs(SECTIONS)
    for i, sec in enumerate(SECTIONS):
        with sec_tabs[i]:
            render_section(sec)

    st.divider()
    if st.button("Submit Full Exam"):
        submit_exam()

def render_section(section):
    questions = st.session_state.exam[section]
    if st.session_state.section != section:
        st.session_state.section = section
        st.session_state.q_index = 0

    q_index = st.session_state.q_index
    q = questions[q_index]

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"#### {section} - Question {q_index+1}")
        st.markdown(f"**{q['Question']}**")
        prev_ans = st.session_state.answers.get(q["QID"])
        choice = st.radio(
            "Select answer:",
            q["shuffled"],
            index=q["shuffled"].index(prev_ans) if prev_ans in q["shuffled"] else 0,
            key=f"{section}_{q_index}"
        )
        st.session_state.answers[q["QID"]] = choice

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("⬅ Previous", key=f"prev_{section}") and q_index > 0:
                st.session_state.q_index -= 1
                st.rerun()
        with c2:
            if st.button("Clear", key=f"clear_{section}"):
                st.session_state.answers.pop(q["QID"], None)
                st.rerun()
        with c3:
            if st.button("Mark for Review", key=f"review_{section}"):
                st.session_state.review.add(q["QID"])
                st.rerun()
        with c4:
            if st.button("Save & Next", key=f"next_{section}") and q_index < len(questions)-1:
                st.session_state.q_index += 1
                st.rerun()

    with col2:
        st.markdown("#### Question Palette")
        for i, ques in enumerate(questions):
            qid = ques["QID"]
            if qid in st.session_state.review:
                color = "#9b59b6"
            elif qid in st.session_state.answers:
                color = "#2ecc71"
            else:
                color = "#e74c3c"
            if st.button(f"{i+1}", key=f"{section}_nav_{i}"):
                st.session_state.q_index = i
                st.rerun()
            st.markdown(f"<div style='height:6px;background:{color};border-radius:4px;margin-bottom:6px'></div>", unsafe_allow_html=True)

def submit_exam():
    sheet = open_sheet(SHEET_ID)
    users_ws = sheet.worksheet("Users")
    resp_ws = sheet.worksheet("Responses")

    scores = {sec:0 for sec in SECTIONS}

    for sec in SECTIONS:
        for q in st.session_state.exam[sec]:
            selected = st.session_state.answers.get(q["QID"], "")
            correct = q["Correct"]
            if selected == correct:
                scores[sec] += 1
            resp_ws.append_row([
                st.session_state["user"]["Email"],
                q["QID"],
                sec,
                selected,
                correct,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

    total = sum(scores.values())

    users = users_ws.get_all_records()
    for i, u in enumerate(users):
        if u["Email"] == st.session_state["user"]["Email"]:
            users_ws.update(f"F{i+2}:J{i+2}", [[
                scores["Physics"], scores["Chemistry"], scores["Maths"], total, "YES"
            ]])
            break

    st.success("Exam submitted successfully!")
    st.info("Scores are confidential and will not be shown to students.")
