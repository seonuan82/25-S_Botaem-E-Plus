import streamlit as st
from utility.supabase import get_all_records

st.title("📂 전체 사용 내역")

records = get_all_records(user_id=st.session_state['user']['id'])

st.dataframe(records)
