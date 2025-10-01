from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

import os
#from glob import glob
from pprint import pprint
#import json
from typing import List, TypedDict

# Langsmith tracing 여부를 확인 
#print(os.getenv('LANGSMITH_TRACING'))

# Langfuse 사용 여부
f_use_langfuse = False

# 로그 출력 여부
f_print_log = True

# 최종 결과에 상태 정보 포함 출력 여부
f_print_state = False

# 에이전트 사용 여부
f_use_agent = False

# 공통으로 사용한 LLM 인스턴스 생성
llm = ChatOpenAI(model="gpt-4.1-mini")

# 로컬 SQL 데이터베이스 이름
DB_TUNIVERSE = 'tuniverse_integration_hist_database.db'
# 로컬 SQL 데이터베이스 제휴연동 이력 테이블 이름
TABLE_TUNIVERSE_AFF_HIST = 'aff_if_hist'
# 로컬 SQL 데이터베이스 고객(회원) 정보 테이블 이름
TABLE_TUNIVERSE_MEM_LIST = 'mem_info_list'

class ServiceState(TypedDict):
    service_type: str
    need_to_revise: bool
    user_question: str
    retriever_type: str
    embedding_type: str
    sql_query: str
    search_results: List[str]
    final_answer: str

def create_multiline_text(*args):
    return "\n".join(args)

def merge_state(state: ServiceState) -> str:
    """ 최종 화면 출력에 STATE 정보를 포함하여 노출하기 위한 텍스트를 생성 """
    result = create_multiline_text(
        "-----------------------------------------------",
        "   State Info.  ",
        "-----------------------------------------------",
        f"- service_type : {state["service_type"]}",
        f"- user_question : {state["user_question"]}",
        f"- retriever_type : {state["retriever_type"]}",
        f"- embedding_type : {state["embedding_type"]}",
        f"- sql_query : {state["sql_query"]}",
        f"- search_results : {state["search_results"]}",
        "-----------------------------------------------",
        "   Final Answer  ",
        f"{state["final_answer"]}",
        "-----------------------------------------------"
    )    
    return result

def show_state(state: ServiceState):
    """ 로그 출력시 전체 STATE 값의 노출이 필요한 경우 호출"""
    print("-"*33, " State Info.  ", "-"*33)
    print("- [___]service_type : ", state["service_type"])
    print("- [___]user_question : ", state["user_question"])
    print("- [chn]retriever_type : ", state["retriever_type"])
    print("- [chn]embedding_type : ", state["embedding_type"])
    print("- [aff]sql_query : ", state["sql_query"])
    print("- [aff]search_results : ", state["search_results"])
    print("-"*33, " Final Answer ", "-"*33)
    if len(state["final_answer"]) > 0:
        print(state["final_answer"])
    else:
        print("... Empty ...")        
    print("-"*80)