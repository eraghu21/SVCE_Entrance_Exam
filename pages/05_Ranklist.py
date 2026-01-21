import streamlit as st
import pandas as pd
from sheets import open_sheet

SHEET_ID = st.secrets["sheet_id"]

def app():
    sheet = open_sheet(SHEET_ID)
    df = pd.DataFrame(sheet.worksheet("Users").get_all_records())
    df = df[df["Role"]=="student"]
    df = df.sort_values("Total", ascending=False)
    df["Rank"] = range(1, len(df)+1)
    st.title("🏆 Rank List")
    st.dataframe(df[["Rank","Name","Total"]])
