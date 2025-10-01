from langfuse import get_client
from langfuse.langchain import CallbackHandler

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

haha_llm = ChatOpenAI(model="gpt-4.1-mini")

def haha(user_question:str) -> str:
    """ 답변 생성 함수 """

    response_template = """
    당신은 사용자 입력에 대해 유용한 답변을 제공하는 전문가입니다. 
    사용자 입력: {user_question}
    """

    response_prompt = ChatPromptTemplate.from_template(response_template)
    chain = response_prompt | haha_llm | StrOutputParser()
    
    answer = chain.invoke(
        {
            "user_question": user_question,   # 사용자 입력 (상태에서 가져옴)
        }
    )
    
    return answer

def call_funny(message, history):
    """ main.py 에서 call_me 메소드 대신 이 메소드를 호출하면 일반적인 LLM 답변 모드가 됨 """

    history = history or []
    
      # 그래프 실행
    response = haha(message)
    history.append((message, response))
    
    return history, history