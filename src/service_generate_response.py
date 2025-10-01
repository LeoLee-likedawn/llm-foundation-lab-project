from common import ServiceState, llm, f_print_log, f_use_langfuse
from langfuse import get_client
from langfuse.langchain import CallbackHandler

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# 콜백 핸들러 생성# 콜백 핸들러 생성
langfuse_handler = CallbackHandler()
# Langfuse 클라이언트 초기화
langfuse = get_client()


def gen_res(state: ServiceState) -> ServiceState:
    """ 답변 생성 함수 """

    # 답변 템플릿
    #response_template = """
    #다음 정보를 바탕으로 사용자의 질문에 대한 답변을 생성하세요.
    #검색 결과의 정보를 활용하여 정확하고 유용한 정보를 제공하세요.
    #사용자 입력: {user_question}
    #검색 결과: {search_results}

    #답변:
    #"""

    response_template = """
    당신은 사용자 입력에 대해 검색 결과를 참고하여 유용한 답변을 제공하는 전문가입니다.
    사용자 입력: {user_question}
    검색 결과: {search_results} 
    """

    if f_use_langfuse:
        if f_print_log:
            print("Use lanfuse...")
        
        chat_prompt = langfuse.get_prompt("prompt-generate-response-chat", type="chat")
        langchain_prompt = ChatPromptTemplate.from_messages(
            chat_prompt.get_langchain_prompt()
        )
        langchain_prompt.metadata = {"langfuse_prompt": chat_prompt}   # Langfuse 자동 링크를 위한 메타데이터

        # 체인 생성 및 실행
        chain = langchain_prompt | llm
        final_answer = chain.invoke(
            input={"user_question": state['user_question'], "search_results": state['search_results']},
            config={"callbacks": [langfuse_handler]}  # Langfuse 트레이싱을 위한 콜백
        )
    else:        
        response_prompt = ChatPromptTemplate.from_template(response_template)
        chain = response_prompt | llm | StrOutputParser()
    
        final_answer = chain.invoke(
            {
                "user_question": state['user_question'],   # 사용자 입력 (상태에서 가져옴)
                "search_results": state['search_results'],  # 검색 결과 (상태에서 가져옴)
            }
        )

    state['final_answer'] = final_answer
    if f_print_log:
        print ("final_answer : ", state['final_answer'])

    # 결과를 상태에 저장
    return state