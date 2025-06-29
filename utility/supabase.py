from uuid import uuid4
import streamlit as st
from st_supabase_connection import SupabaseConnection

# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

def login_user(user_id: str, password: str):
    if not user_id or not password:
        return False, None

    result = conn.table("users").select("*").eq("user_id", user_id).execute()
    users = result.data
    print("🔍 조회 결과:", users)

    if not users:
        new_user = {
            "id": str(uuid4()),
            "user_id": user_id,
            "password": password
        }
        try:
            insert_result = conn.table("users").insert(new_user).execute()
            return True, new_user
        except Exception as e:
            print("❌ 삽입 실패:", e)
            return False, None

    user = users[0]
    if user["password"] == password:
        return True, user
    else:
        return False, None




def get_recent_records(user_id: str):
    return (
        conn.table("records")
        .select("*")
        .eq("user_id", user_id)  # 로그인한 사용자만 필터
        .order("date", desc=True)
        .limit(5)
        .execute()
        .data
    )

def get_summary(user_id):
    data = conn.table("records").select("category, amount").eq("user_id", user_id).execute().data
    summary = {}
    for d in data:
        summary[d["category"]] = summary.get(d["category"], 0) + d["amount"]
    return summary

def get_all_records(user_id):
    return conn.table("records").select("*").eq("user_id", user_id).execute().data

def add_record(user_id, category, amount, note):
    conn.table("records").insert({"user_id": user_id, "category": category, "amount": amount, "note": note}).execute()
