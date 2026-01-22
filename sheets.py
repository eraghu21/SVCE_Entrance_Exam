import gspread
import json
from google.oauth2.service_account import Credentials
import streamlit as st

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_client():
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def open_sheet(sheet_id):
    client = get_client()
    return client.open_by_key(sheet_id)
