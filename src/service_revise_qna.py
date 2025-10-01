from common import ServiceState, llm, f_print_log

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def revise_qna(state: ServiceState) -> ServiceState:
    """ 사용자 입력이 질문 영역(제휴사/채널)을 판단하기 부족한 경우 입력 보완 방안을 제공하는 함수 """

    # 사용자의 문의 영역을 분석하기 위한 템플릿
    revise_templet = """
    사용자 입력: {user_question}

    당신은 사용자가 정확한 결과를 응답받을 수 있도록 사용자 입력을 보완하도록 가이드하는 전문가입니다.

    사용자 입력을 통해 다음과 같이 질문 영역을 판단할 수 있습니다.
    - 제휴사(affiliate) 핵심 키워드 : "고객", "가입", "해지", "변경", "결제"
    - 채널(channel) 핵심 키워드 : "오류", "조회"

    질문 영역이 제휴사(affiliate)라고 판단되면 다음 정보를 보완할 수 있도록 가이드하세요.
    - 제휴사(affiliate) 핵심 정보 : 고객번호(mbr_num)와 상품명(sku_id) 또는 계약번호(ctr_num) 또는 계약서비스번호(ctr_svc_num)
    - 제휴사(affiliate) 부가 정보 : 연동유형(가입/해지/갱신/변경 등)
    
    질문 영역이 채널(channel)이라고 판단되면 다음 정보를 보완할 수 있도록 가이드하세요.
    - 채널(channel) 핵심 정보 : 오류코드(400,401,403,404,500 등) 또는 오류메시지(Access Restricted, Forbidden, Unauthorized 등)
    - 제휴사(affiliate) 부가 정보 : API키(api_key) 또는 호출 서버 IP 주소 혹은 호출 서버 referer

    질문 영영을 판단할 수 없다면 다음 정보를 영역별(제휴사(affiliate) 또는 채널(channel))로 보완할 수 있도록 가이드하세요.
    - 제휴사(affiliate) 핵심 정보 : 고객번호(mbr_num)와 상품명(sku_id) 또는 계약번호(ctr_num) 또는 계약서비스번호(ctr_svc_num)
    - 제휴사(affiliate) 부가 정보 : 연동유형(가입/해지/갱신/변경 등)
    - 채널(channel) 핵심 정보 : 오류코드(400,401,403,404,500 등) 또는 오류메시지(Access Restricted, Forbidden, Unauthorized 등)
    - 제휴사(affiliate) 부가 정보 : API키(api_key) 또는 호출 서버 IP 주소 혹은 호출 서버 referer
    
    답변:
    """

    # 사용자 입력을 보완할 방안을 제공
    analyze_prompt = ChatPromptTemplate.from_template(revise_templet)
    analyze_chain = analyze_prompt | llm | StrOutputParser()
    result = analyze_chain.invoke({"user_question": state['user_question']})
    final_answer = result.strip().lower()
    
    state['final_answer'] = final_answer
    if f_print_log:
        print ("final_answer : ", state['final_answer'])
   
    # 결과를 상태에 업데이트 
    return state