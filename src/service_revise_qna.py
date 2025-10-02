from common import ServiceState, llm, f_print_log, f_use_langfuse
from langfuse import get_client
from langfuse.langchain import CallbackHandler

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# 콜백 핸들러 생성# 콜백 핸들러 생성
langfuse_handler = CallbackHandler()
# Langfuse 클라이언트 초기화
langfuse = get_client()

def revise_qna(state: ServiceState) -> ServiceState:
    """ 사용자 입력이 질문 영역(제휴사/채널)을 판단하기 부족한 경우 입력 보완 방안을 제공하는 함수 """
    if f_print_log:
        print("-"*80)
        print("Start revise_qna...")
        
    # 사용자의 문의 영역을 분석하기 위한 템플릿
    #revise_templet = """
    #사용자 입력: {user_question}

    #당신은 사용자가 정확한 결과를 응답받을 수 있도록 사용자 입력을 보완하도록 가이드하는 전문가입니다.

    #사용자 입력을 통해 다음과 같이 질문 영역을 판단할 수 있습니다.
    #- 제휴사(affiliate) 핵심 키워드 : "고객", "가입", "해지", "변경", "결제"
    #- 채널(channel) 핵심 키워드 : "오류", "조회"

    #질문 영역이 제휴사(affiliate)라고 판단되면 다음 정보를 보완할 수 있도록 가이드하세요.
    #- 제휴사(affiliate) 핵심 정보 : 고객번호(mbr_num)와 상품명(sku_id) 또는 계약번호(ctr_num) 또는 계약서비스번호(ctr_svc_num)
    #- 제휴사(affiliate) 부가 정보 : 연동유형(가입/해지/갱신/변경 등)
    
    #질문 영역이 채널(channel)이라고 판단되면 다음 정보를 보완할 수 있도록 가이드하세요.
    #- 채널(channel) 핵심 정보 : 오류코드(400,401,403,404,500 등) 또는 오류메시지(Access Restricted, Forbidden, Unauthorized 등)
    #- 제휴사(affiliate) 부가 정보 : API키(api_key) 또는 호출 서버 IP 주소 혹은 호출 서버 referer

    #질문 영영을 판단할 수 없다면 다음 정보를 영역별(제휴사(affiliate) 또는 채널(channel))로 보완할 수 있도록 가이드하세요.
    #- 제휴사(affiliate) 핵심 정보 : 고객번호(mbr_num)와 상품명(sku_id) 또는 계약번호(ctr_num) 또는 계약서비스번호(ctr_svc_num)
    #- 제휴사(affiliate) 부가 정보 : 연동유형(가입/해지/갱신/변경 등)
    #- 채널(channel) 핵심 정보 : 오류코드(400,401,403,404,500 등) 또는 오류메시지(Access Restricted, Forbidden, Unauthorized 등)
    #- 제휴사(affiliate) 부가 정보 : API키(api_key) 또는 호출 서버 IP 주소 혹은 호출 서버 referer
    
    #답변:
    #"""

    revise_template = """
    사용자 입력: {user_question}

    당신은 사용자가 원하는 결과를 응답받을 수 있도록 사용자 입력을 보완하도록 가이드하는 전문가입니다.

    사용자 입력의 다음 키워드 포함 여부로 질문 영역을 추측할 수 있습니다.
    - 제휴사 영역 : "고객", ""가입", "해지", "변경", "결제"
    - 채널 영역 : "오류", "조회"

    질문 영역이 "제휴사" 영역이라고 판단되면 다음 조건에 맞는 정보를 사용자가 질문에 추가할 수 있도록 구체적으로 가이드하세요.
    [조건 2-1] 계약번호(3으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능
    [조건 2-2] 계약서비스번호(6으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능
    [조건 2-3] 고객(회원)이름(한글2자이상)과 이동전화번호(010으로 시작하는 "-"제외한 11자리 숫자), 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능
    [조건 2-4] 고객(회원)번호(1,8,9 로 시작하는 10자리 숫자)와 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능

    질문 영역이 "채널" 영역이라고 판단되면 다음 조건에 맞는 정보를 사용자가 질문에 추가할 수 있도록 구체적으로 가이드하세요.
    [조건 1-1] 오류코드(400,401,403,404,500과 같은 399보다 크고 600보다 작은 3자리 숫자)가 존재하는 경우 "채널" 영역으로 판단
    [조건 1-2] 오류메시지(Access Restricted, Forbidden, Unauthorized, Bad Request, Not Found, Internal Server Error)가 존재하는 경우 "채널" 영역으로 판단

    질문 영역을 판단할 수 없다면 질문 영역별로 위 제시된 조건에 맞는 정보를 질문에 추가할 수 있도록 구체적으로 가이드하세요. (제휴사, 채널 영역 분리하여 모두 가이드)
    """

    if f_use_langfuse:
        if f_print_log:
            print("Use lanfuse...")
        
        chat_prompt = langfuse.get_prompt("prompt-revise-question-chat", type="chat")
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
        final_answer = result.strip().lower()
    else:
        revise_prompt = ChatPromptTemplate.from_template(revise_template)
        chain = revise_prompt | llm | StrOutputParser()
        if f_print_log:
            print("Invoke chain...")
            
        result = chain.invoke({"user_question": state['user_question']})
        final_answer = result.strip().lower()
    
    state['final_answer'] = final_answer
    if f_print_log:
        print ("--- final_answer : ", state['final_answer'])
   
    # 결과를 상태에 업데이트 
    return state