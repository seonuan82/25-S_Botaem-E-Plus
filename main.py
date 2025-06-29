import streamlit as st
from utility.supabase import login_user, get_recent_records, get_summary
from utility.chat import get_today_tip
import matplotlib.pyplot as plt
from uuid import uuid4

st.set_page_config(page_title="보탬 E 플러스", layout="wide")
st.title("보탬 E 플러스")

# 총 보조금 상수
TOTAL_SUBSIDY = 500_000

# --- 로그인 상태 확인 ---
if 'user' not in st.session_state:
    with st.form("login_form"):
        st.subheader("로그인")
        user_id = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")

        if submitted:
            success, user = login_user(user_id, password)
            if success:
                st.session_state['user'] = user
                st.success("로그인에 성공했습니다!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")
    st.stop()

# 로그인된 사용자 정보
user = st.session_state['user']
user_id = user['id']


# 로그인 후 정보 표시
st.markdown("---")
st.subheader(f"{user_id}님, 환영합니다!")

tab1, tab2, tab3, tab4 = st.tabs(["📋 사용 내역", "새 입력", "전체 내역", "챗봇에게 질문"])

with tab1:
    col1, col2 = st.columns([1, 2])
    
    # 최근 사용 내역
    with col1:
        st.markdown("### 최근 사용 내역")
        try:
            recent = get_recent_records(user_id=user_id)
            if recent:
                for r in recent:
                    st.write(f"- {r['category']} : {r['amount']}원")
            else:
  비", "기타"])
    amount = st.number_input("금액", min_value=0)
    note = st.text_input("비고")  # 선택 사항
    submitted = st.form_submit_button("입력")

    if submitted:
        try:
            add_record(user_id=user_id, category=category, amount=amount, note=note)
            st.success("사용 내역이 저장되었습니다.")
            st.rerun()
        except Exception as e:
            st.error("저장에 실패했습니다.")
            st.exception(e)

with tab3:
    st.subheader("전체 사용 내역")
    st.markdown("### 최근 사용 내역")
        try:
            recent = get_recent_records(user_id=user_id)
            if recent:
                for r in recent:
                    st.write(f"- {r['category']} : {r['amount']}원")

with tab4:
    st.subheader("챗봇에게 질문")
    # 챗봇 기능
    if st.button("챗봇 시작하기"):
        tip = get_today_tip()
        st.info(f"🤖 오늘의 팁: {tip}")
