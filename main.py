import streamlit as st
import time
from utility.supabase import login_user

def show_logo():
    st.image("images/logo.png", use_container_width=True)
    time.sleep(3)

def show_login_form():
    st.title("로그인")
    ID = st.text_input("ID")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        success, session = login_user(ID, password)
        if success:
            st.session_state['user'] = session
            st.switch_page("pages/Main_Page.py")
        else:
            st.error("로그인 실패. 다시 시도해주세요.")

if 'user' not in st.session_state:
    show_logo()
    show_login_form()
else:
    st.switch_page("pages/Main_Page.py")
