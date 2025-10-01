from common import ServiceState, llm, f_print_log

from typing import Literal
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langfuse import get_client
from langfuse.langchain import CallbackHandler


def gen_res(state: ServiceState) -> ServiceState:
    """ 답변 생성 함수 """

    # 답변 템플릿
    response_template = """
    다음 정보를 바탕으로 사용자의 질문에 대한 답변을 생성하세요.
    검색 결과의 정보를 활용하여 정확하고 유용한 정보를 제공하세요.
    사용자 입력: {user_question}
    검색 결과: {search_results}

    답변:
    """

    # 답변 생성
    response_prompt = ChatPromptTemplate.from_template(response_template)
    response_chain = response_prompt | llm | StrOutputParser()
    
    final_answer = response_chain.invoke(
        {
            "user_question": state['user_question'],   # 사용자 입력 (상태에서 가져옴)
            "search_results": state['search_results'],  # 검색 결과 (상태에서 가져옴)
            #"language": "한국어" if state['qna_type'] else "영어" # 언어 정보
        }
    )

    state['final_answer'] = final_answer
    if f_print_log:
        print ("final_answer : ", state['final_answer'])

    # 결과를 상태에 저장
    return state