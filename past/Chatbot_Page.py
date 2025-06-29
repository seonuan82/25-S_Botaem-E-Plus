import streamlit as st
from utility.chat import get_chat_response, get_chat_history

st.title("💬 챗봇과 대화하기")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("이전 대화")
    history = get_chat_history(user_id=st.session_state['user']['id'])
    for msg in history:
        st.write(f"🧑: {msg['user']}")
        st.write(f"🤖: {msg['bot']}")

with col2:
    st.subheader("대화하기")
    user_input = st.text_input("질문을 입력하세요.")
    if st.button("전송"):
        response = get_chat_response(user_input)
        st.write(f"🤖: {response}")
