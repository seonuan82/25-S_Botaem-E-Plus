import streamlit as st
from utility.supabase import get_recent_records, get_summary
import matplotlib.pyplot as plt
from utility.chat import get_today_tip

st.title("보탬 E 플러스")

# 로그인 체크
if 'user' not in st.session_state:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    st.switch_page("main.py")

user_id = st.session_state['user']['user_id']
TOTAL_SUBSIDY = 500_000  # 총 보조금

# Layout
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
        st.error("사용 내역을 불러오는 데 문제가 발생했습니다.")
        st.exception(e)

    st.button("내역 추가", on_click=lambda: st.switch_page("pages/Add_Record.py"))
    st.button("전체보기", on_click=lambda: st.switch_page("pages/All_Records.py"))

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
            st.info("사용 내역이 없어 그래프를 표시할 수 없습니다.")
            sizes = []

        used_total = sum(sizes)
        remaining = TOTAL_SUBSIDY - used_total

        st.metric("총 보조금", f"{TOTAL_SUBSIDY:,}원")
        st.metric("남은 보조금", f"{remaining:,}원")
    except Exception as e:
        st.error("사용 현황을 불러오는 데 문제가 발생했습니다.")
        st.exception(e)

# Chatbot tip balloon
if st.button("💡"):
    try:
        tip = get_today_tip()
        st.info(f"💬 오늘의 팁: {tip}")
    except Exception as e:
        st.error("팁을 불러오는 데 실패했습니다.")

