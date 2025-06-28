import streamlit as st
from utility.supabase import get_recent_records, get_summary
import matplotlib.pyplot as plt
from utility.chat import get_today_tip

st.title("보탬 E 플러스")
if 'user' not in st.session_state:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    st.switch_page("main.py")

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("최근 사용 내역")
    recent = get_recent_records(user_id=st.session_state['user']['id'])
    for r in recent:
        st.write(f"- {r['category']}: {r['amount']}원")

    st.button("내역 추가", on_click=lambda: st.switch_page("pages/Add_Record.py"))
    st.button("전체보기", on_click=lambda: st.switch_page("pages/All_Records.py"))

with col2:
    st.subheader("카테고리별 사용 현황")
    summary = get_summary(user_id=st.session_state['user']['id'])
    labels = list(summary.keys())
    sizes = list(summary.values())

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    st.pyplot(fig)

    st.metric("총 보조금", "500,000원")
    st.metric("남은 보조금", "220,000원")

# Chatbot tip balloon
if st.button("💡"):
    tip = get_today_tip()
    st.info(f"💬 오늘의 팁: {tip}")
