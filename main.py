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
    st.subheader("로그인")
    user_id = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        success, user = login_user(user_id, password)
        if success:
            st.session_state['user'] = user
            st.success("로그인 성공!")
            st.stop()
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")
    st.stop()  # 로그인 안됐으면 뒤 코드 실행 중단

# --- 로그인 후 화면 ---
user = st.session_state['user']
user_id = user.get('user_id') or user.get('id')

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("최근 사용 내역")
    try:
        recent = get_recent_records(user_id=user_id)
        if recent:
            for r in recent:
                st.write(f"- {r['category']}: {r['amount']}원")
        else:
            st.info("사용 내역이 없습니다.")
    except Exception as e:
        st.error("사용 내역을 불러오는 데 실패했습니다.")
        st.exception(e)

    if st.button("내역 추가"):
        st.info("내역 추가 페이지는 향후 구현 예정입니다.")

    if st.button("전체 보기"):
        st.info("전체 보기 페이지는 향후 구현 예정입니다.")

with col2:
    st.subheader("카테고리별 사용 현황")
    try:
        summary = get_summary(user_id=user_id)
        if summary:
            labels = list(summary.keys())
            sizes = list(summary.values())
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
            st.pyplot(fig)
        else:
            st.info("사용 내역이 없어 차트를 표시할 수 없습니다.")
            sizes = []

        used_total = sum(sizes)
        remaining = TOTAL_SUBSIDY - used_total

        st.metric("총 보조금", f"{TOTAL_SUBSIDY:,}원")
        st.metric("남은 보조금", f"{remaining:,}원")
    except Exception as e:
        st.error("요약 정보를 불러오는 데 실패했습니다.")
        st.exception(e)

# --- 오늘의 팁 ---
if st.button("💡 오늘의 팁"):
    try:
        tip = get_today_tip()
        st.info(f"💬 {tip}")
    except Exception as e:
        st.error("팁을 불러오는 데 실패했습니다.")
