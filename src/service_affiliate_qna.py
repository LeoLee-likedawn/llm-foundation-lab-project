from common import ServiceState, f_print_log, f_use_agent, show_state, llm
from common import DB_TUNIVERSE

from typing import List, TypedDict
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain_core.prompts import ChatPromptTemplate
from typing import Annotated, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from typing_extensions import TypedDict, Annotated
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# LLM 인스턴스 생성
#llm = ChatOpenAI(model="gpt-4.1")

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]
    #result: Annotated[str, ..., "Result of the query."]

@tool
def user_search(user_question: str) -> str:
    """ 고객(회원)의 정확한 고객(회원) 번호를 추출"""   
    if f_print_log:
        print("-"*80)
        print("Start TOOL(user_search)...")

    query_prompt_template = ChatPromptTemplate.from_messages([
        ("system", 
        """
        사용자 입력: {user_question}
        대상 테이블 : "mem_info_list"
        
        당신은 사용자 입력을 통해 기본적인 정보를 확인하고 이를 이용해 DB의 대상 테이블에서 고객(회원) 번호를 조회하는 쿼리를 작성하는 도구입니다.
        올바른 {dialect} 쿼리를 작성하고 반환하세요.        

        사용자 입력에는 다음 정보가 있을 수 있습니다.
        - 고객번호(회원번호) : 형식 - 1,8,9 로 시작하는 10자리 숫자
        - 고객명(회원명) : 형식 - 한글2자이상
        - 전화번호 : 형식 - 010으로 시작하는 13자리 숫자 ("-"은 무시)

        "mem_info_list" 테이블에는 다음 컬럼과 정보들이 있습니다. 
        - MBR_NUM : 고객번호(회원번호) - 1,8,9 로 시작하는 10자리 숫자
        - MBR_NM : 고객명(회원명) - 한글2자이상
        - MPHON_NUM : 전화번호 - 010으로 시작하는 13자리 숫자 ("-"은 무시)
        - EMIL_ADDR : 이메일주소 - 이메일 형식

        사용자 입력에 있는 정보를 기반으로 "mem_info_list" 테이블에서 고객번호(회원번호)를 조회하는 쿼리를 반환하세요.        
        """),
        ("user", 
        """
        Question:
        {user_question}
        """)
    ])

    query_prompt_template.input_schema.model_json_schema()

    # SQLite 데이터베이스 연결
    db = SQLDatabase.from_uri(f"sqlite:///{DB_TUNIVERSE}")

    if f_print_log:
        print(f"conect database...DB[{DB_TUNIVERSE}]")
        # 사용 가능한 테이블 목록 출력
        print("--- table list ---")
        tables = db.get_usable_table_names()
        for table in tables:
            print("- ",table)
        print("-"*80)    

    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "query": user_question,
            "dialect": db.dialect,
            "table_info": db.get_table_info(),
        }
    )
    
    structured_llm = llm.with_structured_output(QueryOutput)
    if f_print_log:
        print("--- Generate query...")
    sql_query = structured_llm.invoke(prompt)
    query = sql_query["query"]
    if f_print_log:
        print(f"--- Generate query complete...SQL[{query}]")
    
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    
    #search_results = execute_query_tool.invoke(sql_query)
    if f_print_log:
        print(f"--- Excute query tool...SQL[{query}]")
    search_results = execute_query_tool.invoke(query)
    search_results = "고객번호(mbr_num) : " + search_results
    if f_print_log:
        print(f"--- Excute query complete...RES[{search_results}]")
        print("-"*80)

    return search_results

@tool
def hist_search(user_question: str, mbr_num: str) -> List:
    """ 고객(회원)의 상품 사용 이력을 추출 """
    if f_print_log:
        print("-"*80)
        print("Start TOOL(hist_search)...")   

    search_results = []

    query_prompt_template = ChatPromptTemplate.from_messages([
        ("system", 
        """
        사용자 입력: {user_question}
        고객(회원) 번호 : {mbr_num}
        대상 테이블 : "aff_if_hist"
        
        당신은 사용자 입력을 통해 기본적인 정보를 확인하고 이를 이용해 DB의 대상 테이블에서 고객(회원)의 상품 사용 이력을 조회하는 쿼리를 작성하는 도구입니다.
        올바른 {dialect} 쿼리를 작성하고 반환하세요.        

        "aff_if_hist" 테이블에는 다음 컬럼과 정보들이 있습니다.
        - AUDIT_DTM : 연동이력 발생일시
        - AUDIT_ID : 처리자ID
        - MBR_NUM : 고객번호
        - MBR_NM : 고객명
        - CTR_NUM : 계약번호
        - CTR_SVC_NUM : 계약서비스번호
        - AFFC_BZR_NM : 제휴사명 - 상품을 제공하는 회사명으로 고객이 인지하는 정보와 정확하게 일치하지 않을 수 있으니 유사한 값으로 조회 필요
        - AFFC_LNKG_TSK_CD : 업무유형
        --- Q2 : 자동인증가능여부조회
        --- A1 : 가입준비
        --- A2 : 가입
        --- Q3 : 해지가능여부조회
        --- Z1 : 해지
        --- Z3 : 해지취소
        --- CO : 계약연장
        --- CN : 연장취소
        - AFFC_LNKG_TRMS_CD : 연동유형
        --- SB_RQ : T우주 처리 요청
        --- SB_RS : T우주 처리 결과 응답
        --- BS_RQ : 제휴사 처리 요청
        --- BS_RS : 제휴사 처리 결과 응답
        --- BS_AF : 제휴사 처리 결과 T우주 내부 전달
        - TRMS_RSLT_CD : 결과코드
        --- S : 성공
        --- F : 실패
        - TRMS_ERR_CD : 에러코드
        - TRMS_ERR_MSG_CTT : 에러메시지
        - TRMS_REQ_CNTT : 요청전문 - 요청에 사용된 JSON 형태의 전문
        - TRMS_RES_CNTT : 응답전문 - 요청에 대한 응답으로 사용된 JSON 형태의 전문
        - PRD_ID : 패키지ID - 실제 고객이 사용하는 단위 상품들의 묶음 상품의 ID로 10자리 문자열(PR로 시작)로 조회시 정확하게 일치해야 함
        - PRD_NM : 패키지명 - 계약번호와 연결되는 실제 고객이 사용하는 단위 상품들의 묶음 상품명(패키지 상품명)으로 고객이 인지하는 정보와 정확하게 일치하지 않을 수 있으니 유사한 값으로 조회 필요
        - SKU_ID : 상품ID - 실제 고객이 사용하는 단위 상품의 ID로 10자리 문자열(SU로 시작)로 조회시 정확하게 일치해야 함
        - SKU_NM : 상품명 - 계약서비스번호와 매핑되는 실제 고객이 사용하는 단위 상품명으로 고객이 인지하는 정보와 정확하게 일치하지 않을 수 있으니 유사한 값으로 조회 필요

        사용자 입력에 있는 정보를 기반으로 "aff_if_hist" 테이블에서 고객번호(회원번호)를 조회하는 쿼리를 반환하세요.        
        """),
        ("user", 
        """
        Question:
        {user_question}
        """)
    ])

    query_prompt_template.input_schema.model_json_schema()

    # SQLite 데이터베이스 연결
    db = SQLDatabase.from_uri(f"sqlite:///{DB_TUNIVERSE}")

    if f_print_log:
        print(f"conect database...DB[{DB_TUNIVERSE}]")
        # 사용 가능한 테이블 목록 출력
        print("--- table list ---")
        tables = db.get_usable_table_names()
        for table in tables:
            print("- ",table)
        print("-"*80)    

    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "query": user_question,
            "mbr_num": mbr_num,
            "dialect": db.dialect,
            "table_info": db.get_table_info(),
        }
    )
    #print("!!! prompt : ", prompt)
    structured_llm = llm.with_structured_output(QueryOutput)
    if f_print_log:
        print("--- Generate query...")
    sql_query = structured_llm.invoke(prompt)
    query = sql_query["query"]
    if f_print_log:
        print(f"--- Generate query complete...SQL[{query}]")
    
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    
    #search_results = execute_query_tool.invoke(sql_query)
    if f_print_log:
        print(f"--- Excute query tool...SQL[{query}]")
    search_results = execute_query_tool.invoke(query)
    if f_print_log:
        print(f"--- Excute query complete...RES[{search_results}]")
        print("-"*80)
        
    return search_results

def aff_svc_qna_using_agent(state: ServiceState) -> ServiceState:
    """ 채널 연동 관련 오류 원인을 조사하는 함수 """
    if f_print_log:
        print("-"*80)
        print("Start aff_svc_qna_using_agent...")
    
    # 도구 목록
    tools = [user_search, hist_search]  

    # OpenAI GPT-4.1-mini 모델 사용
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    # 도구 실행 에이전트 생성
    search_agent = create_react_agent(llm, tools=tools)

    if f_print_log:
        print("--- Invoke react agent...")
    # 도구 실행 에이전트 사용
    search_results = search_agent.invoke(
        {"messages": [
            ("system", 
            """
            당신은 사용자 입력을 기반으로 사용자의 상품 사용 이력을 조사하고 제공하는 에이전트입니다.
            주어진 도구를 활용하여 사용자가 필요한 정보를 찾아서 제공해야 합니다.
            
            [도구(tool) 사용 전략]
            - user_search : 고객(회원)번호(mbr_num)이 분명하지 않은 경우 사용 (고객명(mbr_nm)와 전화번호(mphon_num) 정보가 있는 경우 사용
            - hist_search : 고객(회원)번호(mbr_num)와 상품정보가 함께 존재하거나 계약번호 혹은 계약서비스번호가 존재하는 경우 사용
            - "user_search"는 필요시 선택적으로 사용하고 "hist_search"는 마지막에 필수적으로 사용해야 합니다.
            """),
            ("human", "{user_question}에 대한 이력 정보를 제공해 주세요.")
            ]
        }
    )
    if f_print_log:
        print(f"--- Invoke react agent complete...RES[{search_results}]")

    state['search_results'] = search_results
    if f_print_log:
        print ("search_results : ", state['search_results'])

    # 결과를 상태에 업데이트 
    return state


def aff_svc_qna_simple(state: ServiceState) -> ServiceState:
    if f_print_log:
        print("-"*80)
        print("Start aff_svc_qna_simple...")

    query_prompt_template = ChatPromptTemplate.from_messages([
        ("system", 
        """
        당신은 SQL 데이터베이스와 상호작용하도록 설계된 에이전트입니다.
        입력된 질문을 기반으로 구문적으로 올바른 {dialect} 쿼리를 작성하고 반환하는 에이전트입니다.
        
        입력된 질문으로 쿼리를 작성할 때에는 반드시 아래에서 제공하는 컬럼명과 컬럼값에 의미와 참고사항을 고려하여 작성해야 합니다.
        "-" 기호 뒤에 나오는 값은 테이블의 컬럼명과 그 의미와 참고사항입니다. (예시 : - 컬럼명 : 의미 - 참고사항)
        "---" 기호는 바로 위 컬럼의 값으로 등장할 수 있는 값과 그 의미입니다. (예시 : --- 컬럼값 : 의미 - 참고사항)
        - AUDIT_DTM : 연동이력 발생일시
        - AUDIT_ID : 처리자ID
        - MBR_NUM : 고객번호
        - MBR_NM : 고객명
        - CTR_NUM : 계약번호
        - CTR_SVC_NUM : 계약서비스번호
        - AFFC_BZR_NM : 제휴사명 - 상품을 제공하는 회사명으로 고객이 인지하는 정보와 정확하게 일치하지 않을 수 있으니 유사한 값으로 조회 필요
        - AFFC_LNKG_TSK_CD : 업무유형
        --- Q2 : 자동인증가능여부조회
        --- A1 : 가입준비
        --- A2 : 가입
        --- Q3 : 해지가능여부조회
        --- Z1 : 해지
        --- Z3 : 해지취소
        --- CO : 계약연장
        --- CN : 연장취소
        - AFFC_LNKG_TRMS_CD : 연동유형
        --- SB_RQ : T우주 처리 요청
        --- SB_RS : T우주 처리 결과 응답
        --- BS_RQ : 제휴사 처리 요청
        --- BS_RS : 제휴사 처리 결과 응답
        --- BS_AF : 제휴사 처리 결과 T우주 내부 전달
        - TRMS_RSLT_CD : 결과코드
        --- S : 성공
        --- F : 실패
        - TRMS_ERR_CD : 에러코드
        - TRMS_ERR_MSG_CTT : 에러메시지
        - TRMS_REQ_CNTT : 요청전문 - 요청에 사용된 JSON 형태의 전문
        - TRMS_RES_CNTT : 응답전문 - 요청에 대한 응답으로 사용된 JSON 형태의 전문
        - PRD_ID : 패키지ID - 실제 고객이 사용하는 단위 상품들의 묶음 상품의 ID로 10자리 문자열(PR로 시작)로 조회시 정확하게 일치해야 함
        - PRD_NM : 패키지명 - 계약번호와 연결되는 실제 고객이 사용하는 단위 상품들의 묶음 상품명(패키지 상품명)으로 고객이 인지하는 정보와 정확하게 일치하지 않을 수 있으니 유사한 값으로 조회 필요
        - SKU_ID : 상품ID - 실제 고객이 사용하는 단위 상품의 ID로 10자리 문자열(SU로 시작)로 조회시 정확하게 일치해야 함
        - SKU_NM : 상품명 - 계약서비스번호와 매핑되는 실제 고객이 사용하는 단위 상품명으로 고객이 인지하는 정보와 정확하게 일치하지 않을 수 있으니 유사한 값으로 조회 필요
        
        작업을 시작할 때는 항상 데이터베이스의 테이블 목록을 확인해야 합니다.
        이 단계를 건너뛰지 마십시오.
        {table_info}
        """),
        ("user", 
        """
        Question:
        {query}
        """)
    ])

    query_prompt_template.input_schema.model_json_schema()

    # SQLite 데이터베이스 연결
    db = SQLDatabase.from_uri(f"sqlite:///{DB_TUNIVERSE}")

    if f_print_log:
        print(f"conect database...DB[{DB_TUNIVERSE}]")
        # 사용 가능한 테이블 목록 출력
        print("--- table list ---")
        tables = db.get_usable_table_names()
        for table in tables:
            print("- ",table)
        print("-"*80)    

    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "query": state["user_question"],
            "dialect": db.dialect,
            "table_info": db.get_table_info(),
        }
    )
    
    structured_llm = llm.with_structured_output(QueryOutput)
    if f_print_log:
        print("--- Generate query...")
    sql_query = structured_llm.invoke(prompt)

    state['sql_query'] = sql_query["query"]
    if f_print_log:
        print(f"--- Generate query complete...SQL[{state['sql_query']}]")
    #state['sql_query'] = "SELECT * FROM aff_if_hist WHERE CTR_NUM = '3100038198'"
    if f_print_log:
        print(f"--- Generate query complete...SQL[{state['sql_query']}]")
    
    if f_print_log:
        show_state(state)

    execute_query_tool = QuerySQLDatabaseTool(db=db)
    
    #search_results = execute_query_tool.invoke(sql_query)
    if f_print_log:
        print(f"--- Excute query tool...SQL[{state['sql_query']}]")
    search_results = execute_query_tool.invoke(state['sql_query'])
    if f_print_log:
        print(f"--- Excute query complete...RES[{search_results}]")
    
    state['search_results'] = search_results

    #gpt_sql = create_sql_query_chain(llm=llm, db=db)

    # 쿼리 실행
    #test_question = state['user_question']
    #gpt_generated_sql = gpt_sql.invoke({'question':test_question})
    #print(f"Answer (GPT):\n{gpt_generated_sql}")
    #print("-"*100)
    
    if f_print_log:
        show_state(state)

    return state

def aff_svc_qna(state: ServiceState) -> ServiceState:
    """ 제휴사 연동 관련 오류 원인을 조사하는 함수 """
    
    if f_use_agent:
        if f_print_log:
            print("--- aff_svc_qna_using_agent ---")
        state =aff_svc_qna_using_agent(state)    
    else:
        if f_print_log:
            print("--- aff_svc_qna_simple ---")
        state = aff_svc_qna_simple(state)
    
    return state