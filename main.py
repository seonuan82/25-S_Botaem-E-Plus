import streamlit as st
from utility.gsheet import login_user, get_recent_records, get_summary, add_chatlog, get_all_records, add_record
from utility.chat import get_today_tip, get_chat_response, get_chat_history
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from uuid import uuid4
import datetime
from utility.ocr import extract_receipt_info

st.set_page_config(page_title="보탬 E 플러스", layout="wide")
st.image("images/logo1.png",width=200)

# 총 보조금 상수
TOTAL_SUBSIDY = 5_000_000

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
st.subheader(f"{user['user_id']}님, 환영합니다!")

tab1, tab2, tab3, tab4 = st.tabs(["사용 내역", "내역 추가", "전체 내역", "챗봇에게 질문"])

with tab1:
    col1, col2 = st.columns([1, 2])

    # 최근 사용 내역
    with col1:
        st.markdown("### 최근 사용 내역")
        try:
            recent = get_recent_records(user_id=user_id)
            if recent:
                cat, amount = st.columns([1,2])
                with cat:
                    for r in recent:
                        st.markdown(f"<h6 style='text-align: center;'>{r['category']}</h6>", unsafe_allow_html=True) 
                with amount:
                    for r in recent:
                        st.markdown(f"<h6 style='text-align: center;'>{r['amount']}</h6>", unsafe_allow_html=True) 
            else:
                st.info("최근 사용 내역이 없습니다.")
        except Exception as e:
            st.error("사용 내역을 불러오는 중 오류가 발생했습니다.")
            st.exception(e)

        tip = get_today_tip()
        st.info(f"오늘의 팁: {tip}")

    # 사용 요약 및 보조금
    with col2:
        st.markdown("### 카테고리별 사용 현황")
        try:
            summary = get_summary(user_id=user_id)

            if summary:
                labels = list(summary.keys())
                sizes = list(summary.values())
            else:
                # 데이터가 없을 경우 기본 파이차트 데이터
                labels = ['내역 없음']
                sizes = [1]

            font_path = "fonts/NanumGothic.ttf"
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            
            fig, ax = plt.subplots(figsize=(4, 4))
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct='%1.1f%%',
                textprops={'fontproperties': font_prop}
            )

            for text in texts + autotexts:
                text.set_fontproperties(font_prop)
            
            st.pyplot(fig)

            used_total = sum(summary.values()) if summary else 0
            remaining = TOTAL_SUBSIDY - used_total

            st.metric("총 보조금", f"{TOTAL_SUBSIDY:,}원")
            st.metric("남은 보조금", f"{remaining:,}원")
        except Exception as e:
            st.error("요약 정보를 불러오는 중 오류가 발생했습니다.")
            st.exception(e)


with tab2:
    st.subheader("새 사용 내역 입력")

    with st.form("manual_entry_form"):  # 폼 이름 변경
        category = st.selectbox("보조비목", ["인건비", "운영비", "여비", "업무 추진비", "직무 수행 경비", "연구개발비","보전금", "민간이전", "출연금","토지매입비","건설비", "유형 자산","무형 자산","예탁금","정산금","상환"])
        amount = st.number_input("금액", min_value=0)
        note = st.text_input("비고", value="")
        date = st.date_input("사용날짜")
        submitted = st.form_submit_button("입력")

        if submitted:
            success = add_record(
                user_id=user_id,
                category=category,
                amount=amount,
                note=note,
                date=date
            )
            if success:
                st.success("사용 내역이 저장되었습니다.")
                st.rerun()
            else:
                st.error("저장 실패: DB에 삽입되지 않았습니다.")

    # OCR 기능 추가
    st.markdown("### 영수증 OCR로 자동 입력")
    uploaded_image = st.file_uploader("영수증 이미지 업로드", type=["jpg", "jpeg", "png"])

    if uploaded_image:
        try:
            ocr_amount, ocr_date, ocr_note, ocr_text = extract_receipt_info(uploaded_image)
            st.success("OCR 성공: 자동 추출된 정보")
            st.write(f"금액: {ocr_amount}원")
            st.write(f"날짜: {ocr_date}")
            st.write(f"비고: {ocr_note}")
            with st.expander("OCR 전체 텍스트 보기"):
                st.code(ocr_text)

            # OCR 입력용 별도 폼 사용
            with st.form("ocr_entry_form"):
                category = st.selectbox("보조비목", ["인건비", "운영비", "여비", "업무 추진비", "직무 수행 경비", "연구개발비","보전금", "민간이전", "출연금","토지매입비","건설비", "유형 자산","무형 자산","예탁금","정산금","상환"], key="ocr_category")
                note = st.text_input("비고", value=ocr_note, key="ocr_note_input")
                amount = st.number_input("금액", value=ocr_amount, key="ocr_amount_input")
                date = st.date_input("사용날짜", value=ocr_date, key="ocr_date_input")
                submit_ocr = st.form_submit_button("이 내용으로 자동 채우기")

                if submit_ocr:
                    success = add_record(
                        user_id=user_id,
                        category=category,
                        amount=ocr_amount,
                        note=ocr_note,
                        date=ocr_date
                    )
                    if success:
                        st.success("OCR 정보가 저장되었습니다.")
                        st.rerun()
                    else:
                        st.error("저장 실패: DB에 삽입되지 않았습니다.")

        except Exception as e:
            if "BILLING_DISABLED" in str(e):
                st.error("Vision API 사용을 위해 결제 활성화가 필요합니다.")
            else:
                st.error("OCR 처리 중 오류가 발생했습니다.")
                st.exception(e)

with tab3:
    st.subheader("전체 사용 내역")
    try:
        all_records = get_all_records(user_id=user_id)
        if all_records:
            date, cat2, amount2, note = st.columns(4)
            with date:
                for r in recent:
                    st.markdown(f"<p style='text-align: center;'>{r['date']}</p>", unsafe_allow_html=True) 
            with cat2:
                for r in recent:
                    st.markdown(f"<p style='text-align: center;'>{r['category']}</p>", unsafe_allow_html=True) 
            with amount2:
                for r in recent:
                    st.markdown(f"<p style='text-align: center;'>{r['amount']}</p>", unsafe_allow_html=True)  
            with note:
                for r in recent:
                    st.markdown(f"<p style='text-align: center;'>{r['note']}</p>", unsafe_allow_html=True)  
        else:
            st.info("저장된 전체 내역이 없습니다.")
    except Exception as e:
        st.error("전체 내역을 불러오는 중 오류가 발생했습니다.")
        st.exception(e)



with tab4:
    st.subheader("챗봇 '태미'와 대화하기")

    # 세션 상태 초기화
    if "chat_rounds" not in st.session_state:
        st.session_state.chat_rounds = {}

    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = str(uuid4())
        st.session_state.chat_rounds[st.session_state.current_chat_id] = []

    # 새 대화 시작 버튼
    if st.button("새 대화 시작"):
        new_id = str(uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.chat_rounds[new_id] = []

    chat_id = st.session_state.current_chat_id

    # 입력창
    input_key = f"chat_input_{chat_id}"
    user_message = st.text_input("태미미에게 질문해보세요.", key=input_key)
    
    if user_message:
        try:
            bot_response = get_chat_response(user_message)
    
            if chat_id not in st.session_state.chat_rounds:
                st.session_state.chat_rounds[chat_id] = []
    
            st.session_state.chat_rounds[chat_id].append((user_message, bot_response))
    
            add_chatlog(str(user_id), str(chat_id), f"User: {user_message}")
            add_chatlog(str(user_id), str(chat_id), f"Neo: {bot_response}")
    
            del st.session_state[input_key]
    
            st.rerun()
    
        except Exception as e:
            st.error("대화 중 오류가 발생했습니다.")
            st.exception(e)
            
    # 현재 대화 출력
    st.markdown("---")  
    logs = st.session_state.chat_rounds.get(chat_id, [])
    
    if logs:
        chat_html = """
            <div style="max-height: 400px; overflow-y: auto; padding: 10px;">
            <style>
            .bubble-user {
                background-color: #DCF8C6;
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 8px;
                max-width: 75%;
                text-align: left;
                margin-left: auto;
            }
            .bubble-agent {
                background-color: #ABCDDE;
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 8px;
                max-width: 75%;
                text-align: left;
                margin-right: auto;
            }
            </style>
        """
    
        for q, a in logs:
            chat_html += f"""
            <div class="bubble-user">
                <b>당신:</b> {q}
            </div>
            <div class="bubble-agent">
                <b>태미:</b> {a}
            </div>
            """
    
        chat_html += "</div>"
    
        import streamlit.components.v1 as components
        components.html(chat_html, height=420, scrolling=False)
    
    else:
        st.markdown("_아직 대화가 없습니다. 태미에게 말을 걸어보세요!_")


