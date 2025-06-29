from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage

CHAT_PROMPT = """
당신은 다음 법령을 기준으로 사용자의 질문에 답합니다.
당신의 피드백은 다음과 같은 항목을 포함해야 합니다:
1. 법적 근거
2. 사용자의 질문에 대한 답
3. 도움을 받을 수 있는 전화번호

피드백은:
- 100자 이내여야 하고
- 한국어로 제시되어야 하며
- 4수준, 5수준 마크다운 형식을 이용하고
- 명료하고 직접적이며 공손한 표현을 사용해야 함.]
"""

memory = ConversationBufferMemory(k=6, return_messages=True)   # remember up to 3 messages (better user experience:)

# LLM Model
llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)  # or "gpt-4.5-turbo"
conversation = ConversationChain(llm=llm, memory=memory)

def get_today_tip():
    response = conversation.predict(input="사용자에게 재정 팁 하나만 한 줄로 보여줘.")
    return response

def get_chat_response(message):
    full_prompt = CHAT_PROMPT.strip() + "\n\nuser question: " + message
    response = conversation.predict(input=full_prompt)
    return response

def get_chat_history(user_id):
    # 예시 데이터
    return [{"user": "이번 달 예산이 부족해요.", "bot": "지출을 검토해보고 가장 큰 항목을 줄여보세요."}]
