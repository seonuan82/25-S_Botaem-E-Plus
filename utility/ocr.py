import datetime
import re
import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account

@st.cache_resource
def init_vision_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
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
        raise ValueError("No text detected in image.")

    full_text = annotations[0].description  # Full OCR text as string

    # Extract ammount
    amount = 0
    amount_match = re.search(r'(합계|총액|합계금액)[^\d]*(\d{1,3}(,\d{3})*)', full_text)
    if amount_match:
        amount_str = amount_match.group(2).replace(",", "")
        try:
            amount = int(amount_str)
        except ValueError:
            amount = 0

    # Extract date
    date = datetime.date.today()
    date_match = re.search(r'(\d{4}[./-]\d{1,2}[./-]\d{1,2})', full_text)
    if date_match:
        date_str = date_match.group(1).replace(".", "-").replace("/", "-")
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    # Extract note/store name
    lines = [line.strip() for line in full_text.split("\n") if line.strip()]
    note = lines[0] if lines else ""

    return amount, date, note, full_text

    except Exception as e:
        raise RuntimeError(f"OCR 처리 중 오류 발생: {e}")
