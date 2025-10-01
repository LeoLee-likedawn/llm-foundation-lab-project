from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal
from common import ServiceState, llm, f_print_log


def chk_svc_typ(state: ServiceState) -> ServiceState:
    """ 사용자 입력이 질문 영역(제휴사/채널)에 대해 판단하는 함수 """

    # 사용자의 문의 영역을 분석하기 위한 템플릿
    analyze_template = """
    당신은 사용자 입력을 통해 질문 영역을 판단하는 답변하는 전문가입니다.

    제휴사(affiliate) 혹은 채널(channel) 영역의 판단은 다음 제공된 핵심 정보의 포함 여부에 따라 결정합니다.
    구체적인 정보가 존재하지 않는 경우 판단 불가로 판단하고 "unknown"으로 답변하세요.
    - 제휴사(affiliate) 핵심 정보 : 고객번호(mbr_num)와 상품명(sku_id) 또는 계약번호(ctr_num) 또는 계약서비스번호(ctr_svc_num)
    - 채널(channel) 핵심 정보 : 오류코드(400,401,403,404,500 등) 또는 오류메시지(Access Restricted, Forbidden, Unauthorized 등)    

    제휴사(affiliate) 연동과 관련된 질문인 경우 "affiliate"로 답변하세요. 
    채널(channel) 연동과 관련된 질문인 경우 "channel"로 답변하세요.
    판단이 불가한 경우 "unknown"으로 답변하세요.

    사용자 입력: {user_question}

    답변:
    """

    # 사용자 입력을 분석하여 한국어인지 판단
    analyze_prompt = ChatPromptTemplate.from_template(analyze_template)
    analyze_chain = analyze_prompt | llm | StrOutputParser()
    result = analyze_chain.invoke({"user_question": state['user_question']})
    service_type = result.strip().lower()
    
    state['service_type'] = service_type
    if f_print_log:
        print ("SVC TYPE : ", state['service_type'])

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
