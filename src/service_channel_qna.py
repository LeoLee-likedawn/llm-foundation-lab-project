from common import ServiceState, f_print_log
from load_channel_data import initialize_vector_store

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


#에이전트 사용 여부
f_use_agent = False

#Retriever 유형 선택
#retriever_type = "S" #similarity
#f_retriever_type = "M" #mmr
#f_retriever_type = "T" #threshold

@tool
def error_reason_search(state: ServiceState):
    """채널 연동 관련 오류 원인을 DB에서 조회하고 결과를 반환하는 도구"""
    if f_print_log:
        print("-"*80)
        print("Start TOOL(error_reason_search)...")
        
    # 벡터 저장소 초기화
    chroma_db = initialize_vector_store()

    # 커스텀 검색기 생성
    def create_custom_retriever(search_type="similarity", k=5, **kwargs):
        """커스텀 검색기 생성"""
        return chroma_db.as_retriever(
            search_type=search_type,
            k=k,
            **kwargs
        )
    
    # 다양한 검색기 생성
    if state["retriever_type"] == "S":
        chroma_k_retriever = create_custom_retriever("similarity", k=5)
    elif state["retriever_type"] == "M":
        chroma_k_retriever = create_custom_retriever("mmr", k=5, fetch_k=20)
    elif state["retriever_type"] == "T":
        chroma_k_retriever = create_custom_retriever("similarity_score_threshold", score_threshold=0.8)
    else:
        chroma_k_retriever = create_custom_retriever("similarity", k=5)

    search_db = create_retriever_tool(
        chroma_k_retriever,
        name="search_db",
        description="채널 연동 관련 오류와 해결방안에 대해 데이터베이스에서 검색하고 결과를 반환합니다.",
    )
   
    search_results = search_db.invoke(state["user_question"])
    return search_results

### 3-2. 채널 연동 오류 원인 조사 서비스 구현
def chn_svc_qna_using_agent(state: ServiceState) -> ServiceState:
    """ 채널 연동 관련 오류 원인을 조사하는 함수 """
    
    # 도구 목록
    tools = [error_reason_search]  

    # OpenAI GPT-4.1-mini 모델 사용
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    # 도구 실행 에이전트 생성
    search_agent = create_react_agent(llm, tools=tools)

    # 도구 실행 에이전트 사용
    search_results = search_agent.invoke(
        {"messages": [
            ("system", "error_reason_search 도구를 사용"),
            ("human", "{user_question}에 대한 오류 원인을 조사하고 해결방안을 제시해주세요.")
            ]
        }
    )
    state['search_results'] = search_results
    if f_print_log:
        print ("search_results : ", state['search_results'])

    # 결과를 상태에 업데이트 
    return state


### 3-2. 채널 연동 오류 원인 조사 서비스 구현
def chn_svc_qna_simple(state: ServiceState) -> ServiceState:
    """ 채널 연동 관련 오류 원인을 조사하는 함수 """    
   
    # 벡터 저장소 초기화
    chroma_db = initialize_vector_store(state["embedding_type"])

    # 커스텀 검색기 생성
    def create_custom_retriever(search_type="similarity", k=5, **kwargs):
        """커스텀 검색기 생성"""
        return chroma_db.as_retriever(
            search_type=search_type,
            k=k,
            **kwargs
        )

    if state["retriever_type"] == "":
        retriever_type = "S"
    else:
        retriever_type = state["retriever_type"]

    # 다양한 검색기 생성
    if retriever_type == "S":
        chroma_k_retriever = create_custom_retriever("similarity", k=5)
    elif retriever_type == "M":
        chroma_k_retriever = create_custom_retriever("mmr", k=5, fetch_k=20)
    elif retriever_type == "T":
        chroma_k_retriever = create_custom_retriever("similarity_score_threshold", score_threshold=0.8)
    else:
        chroma_k_retriever = create_custom_retriever("similarity", k=5)

    query = state["user_question"]
    search_results = chroma_k_retriever.invoke(query)

    state['search_results'] = search_results
    if f_print_log:
        print ("search_results : ", state['search_results'])

    # 결과를 상태에 업데이트 
    return state

def chn_svc_qna(state: ServiceState) -> ServiceState:
    """ 채널 연동 관련 오류 원인을 조사하는 함수 """
    
    if f_use_agent:
        if f_print_log:
            print("--- chn_svc_qna_using_agent ---")
        state =chn_svc_qna_using_agent(state)    
    else:
        if f_print_log:
            print("--- chn_svc_qna_simple ---")
        state = chn_svc_qna_simple(state)

    # 결과를 상태에 업데이트 
    return state