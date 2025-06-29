import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from uuid import uuid4
from datetime import datetime


def init_sheet():
    scope = ["https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gsheet"], scope
    )
    client = gspread.authorize(credentials)
    return client.open_by_url('https://docs.google.com/spreadsheets/d/1xcDDzaS5rk3jhXbU3215XXYlF2vK9-LTwKqS96f6yq4/edit?gid=0#gid=0') 


def login_user(user_id: str, password: str):
    sheet = init_sheet()
    worksheet = sheet.worksheet("id")
    users = worksheet.get_all_records()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    input_user_id = user_id.strip()
    input_pw = password.strip()

    for user in users:
        stored_user_id = str(user.get("user_id", ""))
        stored_pw = str(user.get("password", ""))

        if stored_user_id == input_user_id:
            if stored_pw == input_pw:
                return True, user
            else:
                return False, None

    # 사용자 ID가 없으면 새 사용자 등록
    new_user = {
        "timestamp": timestamp,
        "id": str(uuid4()),            
        "user_id": input_user_id,      
        "password": input_pw
    }

    # 헤더 순서대로 값 삽입
    worksheet.append_row([
        new_user["timestamp"],
        new_user["id"],
        new_user["user_id"],
        new_user["password"]
    ])

    return True, new_user

    # 새 사용자 등록
    new_user = {
        "timestamp": timestamp,
        "id": str(uuid4()),
        "user_id": user_id.strip(),  # 필요시 사용자 이름 등으로 채우세요
        "password": password.strip()
    }
    worksheet.append_row(list(new_user.values()))
    return True, new_user



def add_record(user_id, category, amount, note, date):
    sheet = init_sheet()
    worksheet = sheet.worksheet("use")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_row = [
            timestamp,
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


def add_chatlog(user_id, chat_id, chat):
    sheet = init_sheet()
    worksheet = sheet.worksheet("chat")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_row = [
        timestamp,
        str(uuid4()),
        user_id,
        chat_id,
        chat
    ]
    worksheet.append_row(new_row)
    return True
