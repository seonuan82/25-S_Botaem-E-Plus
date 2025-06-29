from PIL import Image
import pytesseract
import re
import datetime

def extract_receipt_info(image_file):
    """
    Extract amount, date, and store name (note) from a receipt image.
    Returns: amount (int), date (datetime.date), note (str), full OCR text (str)
    """
    try:
        image = Image.open(image_file)

        # OCR using Korean + English
        text = pytesseract.image_to_string(image, lang='kor+eng')

        # --- 금액 추출 ---
        amount = 0
        amount_match = re.search(r'(합계|총액|합계금액)[^\d]*(\d{1,3}(,\d{3})*)', text)
        if amount_match:
            amount_str = amount_match.group(2).replace(",", "")
            amount = int(amount_str)

        # --- 날짜 추출 ---
        date = datetime.date.today()
        date_match = re.search(r'(\d{4}[./-]\d{1,2}[./-]\d{1,2})', text)
        if date_match:
            date_str = date_match.group(1).replace(".", "-").replace("/", "-")
            try:
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        # --- 비고/상호명 추출 ---
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        note = lines[0] if lines else ""

        return amount, date, note, text

    except Exception as e:
        raise RuntimeError(f"OCR 처리 중 오류 발생: {e}")
