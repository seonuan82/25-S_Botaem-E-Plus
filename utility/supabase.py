import streamlit as st
from st_supabase_connection import SupabaseConnection

# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

def login_user(user_id: str, password: str):
    try:
        result = supabase.table("users").select("*").eq("user_id", user_id).execute()
        users = result.data
        if not users:
            new_user = {
                "user_id": user_id,
                "password": password
            }
            insert_result = supabase.table("users").insert(new_user).execute()
    
            if insert_result.error:
                print("실패:", insert_result.error)
                return False, None
            else:
                return True, new_user
    
        else:
            user = users[0]
            if user["password"] == password:
                return True, user
    except Exception:
        return False, None

def get_recent_records(user_id):
    return supabase.table("records").select("*").eq("user_id", user_id).order("date", desc=True).limit(5).execute().data

def get_summary(user_id):
    data = supabase.table("records").select("category, amount").eq("user_id", user_id).execute().data
    summary = {}
    for d in data:
        summary[d["category"]] = summary.get(d["category"], 0) + d["amount"]
    return summary

def get_all_records(user_id):
    return supabase.table("records").select("*").eq("user_id", user_id).execute().data

def add_record(user_id, category, amount, note):
    supabase.table("records").insert({"user_id": user_id, "category": category, "amount": amount, "note": note}).execute()
