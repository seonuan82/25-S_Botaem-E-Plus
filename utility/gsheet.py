import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from uuid import uuid4
from datetime import datetime


def init_sheet():
    scope = ["https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets[gsheet], scope
    )
    client = gspread.authorize(credentials)
    return client.open_by_url('https://docs.google.com/spreadsheets/d/1xcDDzaS5rk3jhXbU3215XXYlF2vK9-LTwKqS96f6yq4/edit?gid=0#gid=0') 


def login_user(user_id: str, password: str):
    sheet = init_sheet()
    worksheet = sheet.worksheet("id")
    users = worksheet.get_all_records()

    for user in users:
        if user["user_id"] == user_id:
            if user["password"] == password:
                return True, user
            else:
                return False, None

    # 신규 사용자 등록
    new_user = {
        "id": str(uuid4()),
        "user_id": user_id,
        "password": password
    }
    worksheet.append_row(list(new_user.values()))
    return True, new_user



def add_record(user_id, category, amount, note, date):
    sheet = init_sheet()
    worksheet = sheet.worksheet("use")
    new_row = [
        str(uuid4()),
        user_id,
        category,
        amount,
        note,
        date.strftime("%Y-%m-%d")
    ]
    worksheet.append_row(new_row)
    return True



def get_recent_records(user_id):
    sheet = init_sheet()
    worksheet = sheet.worksheet("use")
    records = worksheet.get_all_records()
    user_records = [r for r in records if r["user_id"] == user_id]
    sorted_records = sorted(user_records, key=lambda x: x["date"], reverse=True)
    return sorted_records[:5]


def get_summary(user_id):
    sheet = init_sheet()
    worksheet = sheet.worksheet("use")
    records = worksheet.get_all_records()
    summary = {}
    for r in records:
        if r["user_id"] == user_id:
            cat = r["category"]
            amt = int(r["amount"])
            summary[cat] = summary.get(cat, 0) + amt
    return summary


def get_all_records(user_id):
    sheet = init_sheet()
    worksheet = sheet.worksheet("use")
    records = worksheet.get_all_records()
    return [r for r in records if r["user_id"] == user_id]
