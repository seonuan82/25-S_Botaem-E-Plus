import streamlit as st
from utility.supabase import login_user
from st_supabase_connection import SupabaseConnection

def show_logo():
    st.image("images/logo.png", use_container_width=True)

def show_login_form():
    st.title("로그인")
    user_id = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        success, session = login_user(user_id, password)
        if success:
            st.session_state['user_id'] = session
            st.switch_page("pages/Main_Page.py")
        else:
            st.error("비밀번호가 바르지 않습니다.")

if 'user' not in st.session_state:
    conn = st.connection("supabase",type=SupabaseConnection)
    show_logo()
    show_login_form()
else:
    st.switch_page("pages/Main_Page.py")
