import streamlit as st
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import time

#def chat():
  # chatbot giving useful tips


#def data_storage():
  # storing data -> firebase?



## ------------------------ Page 1 ---------------------------------------##



# Main_보탬e플러스 로고 및 챗봇의 유용한 팁
st.markdown(
    """
    <style>
        button[title^=Exit]+div [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)

st.image("images/temp_logo.png")
time.sleep(5)
st.rerun()
st.stop()

#chatbot 파트 추가하기


## ------------------------- Page 2 --------------------------------------##
st.title('보탬e플러스')

usage, extra = st.columns(2)
with usage:
  st.markdown("사용 내역")

with extra:
  st.markdown("extra")


