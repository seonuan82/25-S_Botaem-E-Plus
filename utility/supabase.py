from supabase import create_client
supabase = create_client(url, key)

def login_user(entered_id, password):
    try:
        result = supabase.auth.sign_in_with_password({"id": entered_id, "password": password})
        return True, result.user
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
