import streamlit as st
from utility.gsheet import login_user, get_recent_records, get_summary, add_record, get_all_records
from utility.chat import get_today_tip
import matplotlib.pyplot as plt
from uuid import uuid4
import datetime
from utility.ocr import extract_receipt_info

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
                for r in recent:
                    st.write(f"- {r['category']} : {r['amount']}원")
            else:
                st.info("최근 사용 내역이 없습니다.")
        except Exception as e:
            st.error("사용 내역을 불러오는 중 오류가 발생했습니다.")
            st.exception(e)

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

            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
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

    uploaded_image = st.file_uploader("영수증 이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
    ocr_amount = 0
    ocr_date = datetime.date.today()
    ocr_note = ""

    if uploaded_image:
        try:
            ocr_amount, ocr_date, ocr_note, ocr_text = extract_receipt_info(uploaded_image)
            st.image(uploaded_image, caption="업로드한 영수증", use_column_width=True)
            st.text_area("OCR 결과", ocr_text, height=200)
            st.success(f"추출된 금액: {ocr_amount:,}원")
            st.success(f"추출된 날짜: {ocr_date}")
            st.info(f"추출된 비고: {ocr_note}")
        except Exception as e:
            st.error("OCR 처리 중 오류가 발생했습니다.")
            st.exception(e)

    with st.form("entry_form"):
        category = st.selectbox("카테고리", ["식비", "교통", "의료", "기타"])
        amount = st.number_input("금액", min_value=0)
        note = st.text_input("비고", value="")
        date = st.date_input("사용날짜")
        submitted = st.form_submit_button("입력")
    
        if submitted:
            success = add_record(
                user_id=user['id'],   # UUID로 통일
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

with tab3:
    st.subheader("전체 사용 내역")
    try:
        all_records = get_all_records(user_id=user_id)
        if all_records:
            for r in all_records:
                st.write(f"- {r['date']} | {r['category']} : {r['amount']}원 ({r['note']})")
        else:
            st.info("저장된 전체 내역이 없습니다.")
    except Exception as e:
        st.error("전체 내역을 불러오는 중 오류가 발생했습니다.")
        st.exception(e)

with tab4:
    st.subheader("챗봇에게 질문")
    # 챗봇 기능
    if st.button("챗봇 시작하기"):
        tip = get_today_tip()
        st.info(f"🤖 오늘의 팁: {tip}")
