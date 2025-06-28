import openai

openai.api_key = "your-openai-key"

def get_today_tip():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "사용자에게 재정 팁 하나만 간단히 제공해줘."}]
    )
    return response.choices[0].message['content']

def get_chat_response(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message['content']

def get_chat_history(user_id):
    # 예시 데이터
    return [{"user": "이번 달 예산이 부족해요.", "bot": "지출을 검토해보고 가장 큰 항목을 줄여보세요."}]
