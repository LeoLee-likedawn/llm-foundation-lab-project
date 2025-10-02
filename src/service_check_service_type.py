from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal
from common import ServiceState, llm, f_print_log, f_use_langfuse
from langfuse import get_client
from langfuse.langchain import CallbackHandler

# 콜백 핸들러 생성# 콜백 핸들러 생성
langfuse_handler = CallbackHandler()
# Langfuse 클라이언트 초기화
langfuse = get_client()

def chk_svc_typ(state: ServiceState) -> ServiceState:
    """ 사용자 입력이 질문 영역(제휴사/채널)에 대해 판단하는 함수 """
    if f_print_log:
        print("-"*80)
        print("Start chk_svc_typ...")

    # 사용자의 문의 영역을 분석하기 위한 템플릿
    #analyze_template = """
    #당신은 사용자 입력을 통해 질문 영역을 판단하는 답변하는 전문가입니다.

    #제휴사 영역 혹은 채널 영역의 판단은 다음 제공된 핵심 정보의 포함 여부에 따라 결정합니다.
    #구체적인 정보가 존재하지 않는 경우 판단 불가로 판단하고 "unknown"으로 답변하세요.
    #- 제휴사 영역 핵심 정보 : 고객번호(mbr_num)와 상품명(sku_id) 또는 계약번호(ctr_num) 또는 계약서비스번호(ctr_svc_num)
    #- 채널(channel) 핵심 정보 : 오류코드(400,401,403,404,500 등) 또는 오류메시지(Access Restricted, Forbidden, Unauthorized 등)    

    #제휴사(affiliate) 연동과 관련된 질문인 경우 "affiliate"로 답변하세요. 
    #채널(channel) 연동과 관련된 질문인 경우 "channel"로 답변하세요.
    #판단이 불가한 경우 "unknown"으로 답변하세요.

    #사용자 입력: {user_question}

    #답변:
    #"""

    analyze_template = """
    사용자 입력: {user_question}
    
    당신은 사용자 입력을 통해 질문 영역을 판단하고 정해진 답변을 제공하는 전문가입니다.
    질문 영역은 "제휴사" 혹은 "채널" 영역이 존재합니다.

    다음 제시된 조건에 하나라도 완전히 부합하는 경우 질문 영역을 판단할 수 있습니다. 반드시 조건에 부합하는지 확인해야 합니다.
    제시된 조건은 각각 독립적이며 완전히 부합하는 조건이 하나도 없는 경우 질문 영역을 판단할 수 없고 이 경우 "unknown"으로 답변합니다.
    제시된 조건은 우선순위의 내림차순이므로 상위 조건 중 완전히 부합하는 조건이 발견되면 하위 조건은 검사하지 않고 영역을 판단하여 답변합니다.
    
    [조건 1-1] 오류코드(400,401,403,404,500과 같은 399보다 크고 600보다 작은 3자리 숫자)가 존재하는 경우 "채널" 영역으로 판단
    [조건 1-2] 오류메시지(Access Restricted, Forbidden, Unauthorized, Bad Request, Not Found, Internal Server Error)가 존재하는 경우 "채널" 영역으로 판단
    [조건 2-1] 계약번호(3으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 영역으로 판단 
    [조건 2-2] 계약서비스번호(6으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 영역으로 판단 
    [조건 2-3] 고객(회원)이름(한글2자이상)과 이동전화번호(010으로 시작하는 "-"제외한 11자리 숫자), 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 영역으로 판단
    [조건 2-4] 고객(회원)번호(1,8,9 로 시작하는 10자리 숫자)와 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 영역으로 판단

    [답변형식]
    "제휴사" 영역이라고 판단되면 "affiliate"로 답변 
    "채널" 영역이라고 판단되면 "channel"로 답변
    아무 조건도 만족하지 않아 판단이 불가하다면 "unknown"으로 답변
    """

    if f_use_langfuse:
        if f_print_log:
            print("Use lanfuse...")

        chat_prompt = langfuse.get_prompt("prompt-check-service-typ-chat", type="chat")
        if f_print_log:
            print(f"--- Get prompt from langfuse...PRT[{chat_prompt}]")

        langchain_prompt = ChatPromptTemplate.from_messages(
            chat_prompt.get_langchain_prompt()
        )
        if f_print_log:
            print(f"--- Generate prompt for langchain...PRT[{langchain_prompt}]")

        langchain_prompt.metadata = {"langfuse_prompt": chat_prompt}   # Langfuse 자동 링크를 위한 메타데이터

        # 체인 생성 및 실행
        chain = langchain_prompt | llm
        if f_print_log:
            print("Invoke chain...")
        result = chain.invoke(
            input={"user_question": state['user_question']},
            config={"callbacks": [langfuse_handler]}  # Langfuse 트레이싱을 위한 콜백
        )
        service_type = result
        if f_print_log:
            print(f"--- Invoke chain complete...SVC_TYPE[{service_type}]")
    else:
        analyze_prompt = ChatPromptTemplate.from_template(analyze_template)
        chain = analyze_prompt | llm | StrOutputParser()

        if f_print_log:
            print("Invoke chain...")
        
        result = chain.invoke({"user_question": state['user_question']})
        service_type = result.strip().lower()
        
        if f_print_log:
            print(f"--- Invoke chain complete...SVC_TYPE[{service_type}]")
    
    state['service_type'] = service_type

    # 결과를 상태에 업데이트 
    return state


def decide_next_step(
        state: ServiceState
    ) -> Literal["aff_svc_qna", "chn_svc_qna", "revise_qna"]:#, "generate_response"]:
    """ 다음 실행 단계를 결정하는 함수 """

    # 한국어인 경우 한국어 문서 검색 함수 실행
    if state['service_type'] == "affiliate":
        return "aff_svc_qna"
    elif state['service_type'] == "channel":
        return "chn_svc_qna"
    else:
        return "revise_qna"  
