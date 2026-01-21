import streamlit as st
import pandas as pd
from sheets import open_sheet

SHEET_ID = st.secrets["sheet_id"]

def app():
    st.title("Admin Dashboard")
    sheet = open_sheet(SHEET_ID)
    df = pd.DataFrame(sheet.worksheet("Users").get_all_records())
    df = df[df["Role"]=="student"]

    st.subheader("Section-wise Average")
    st.bar_chart(df[["Physics","Chemistry","Maths"]].mean())

    st.subheader("Total Score Distribution")
    st.line_chart(df["Total"])

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download Results CSV", csv, "results.csv", "text/csv")

    uploaded = st.file_uploader("Upload Questions Excel", type=["xlsx"])
    if uploaded:
        qdf = pd.read_excel(uploaded)
        qws = sheet.worksheet("Questions")
        for _, row in qdf.iterrows():
            qws.append_row(row.tolist())
        st.success("Questions uploaded successfully")
