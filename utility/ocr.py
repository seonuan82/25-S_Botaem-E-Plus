import datetime
import re
import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account

@st.cache_resource
def init_vision_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gsheet"]
    )
    return vision.ImageAnnotatorClient(credentials=credentials)

def extract_receipt_info(image_file):
    """
    Uses Google Vision API to extract text from receipt image.
    Returns:
      amount (int),
      date (datetime.date),
      note (str),
      full_text (str)
    """
    client = init_vision_client()

    image_bytes = image_file.read()
    image = vision.Image(content=image_bytes)

    response = client.text_detection(image=image)

    if response.error.message:
        raise RuntimeError(f'API Error: {response.error.message}')

    annotations = response.text_annotations
    if not annotations:
        raise ValueError("이미지 내에서 텍스트가 확인되지 않습니다.")

    full_text = annotations[0].description  # Full OCR text as string

    # Extract ammount
    amount = 0
    amount_match = re.search(r'(합계|총액|합계금액)[^\d#₩]*[#₩]?\s*([\d.,]+)', full_text)
    if amount_match:
        amount_str = amount_match.group(2).replace(",", "").replace(".", "")
        try:
            amount = int(amount_str)
        except ValueError:
            amount = 0

    # Extract date
    date = datetime.date.today()
    date_patterns = [
        r"\d{4}[./-]\d{1,2}[./-]\d{1,2}",              # 2024-06-29, 2024.6.29, 2024/06/29
        r"\d{2}[./-]\d{1,2}[./-]\d{1,2}",              # 24.6.29, 29.06.24
        r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일",             # 2024년 6월 29일
        r"\d{1,2}/\d{1,2}/\d{4}",                      # 06/29/2024
        r"\d{4}/\d{1,2}/\d{1,2}",                      # 2024/06/29
        r"\d{1,2}/\d{1,2}/\d{2}",                      # 29/06/24
    ]

    for pattern in date_patterns:
        match = re.search(pattern, full_text)
        if match:
            raw_date = match.group().strip()

            # Handle Korean format: "2024년 6월 29일"
            if "년" in raw_date:
                try:
                    parts = re.findall(r"\d+", raw_date)
                    year, month, day = map(int, parts)
                    date = datetime.date(year, month, day)
                    break
                except Exception:
                    continue
                    
            for fmt in [
                "%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d",
                "%y.%m.%d", "%y-%m-%d", "%y/%m/%d",
                "%m/%d/%Y", "%d/%m/%y"
            ]:
                try:
                    parsed = datetime.datetime.strptime(raw_date, fmt).date()
                    date = parsed
                    break
                except ValueError:
                    continue
            break

    
    # Extract note/store name
    lines = [line.strip() for line in full_text.split("\n") if line.strip()]
    note = lines[0] if lines else ""

    return amount, date, note, full_text
