from langfuse.langchain import CallbackHandler
from langfuse import get_client
from langchain_openai import ChatOpenAI
from langfuse import get_client
from langfuse.langchain import CallbackHandler
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

# 콜백 핸들러 생성
langfuse_handler = CallbackHandler()
# Langfuse 클라이언트 초기화
langfuse = get_client()
# 연결 테스트
#assert langfuse.auth_check()

#로그 출력 여부
f_print_log = False

# 상태 출력 여부
f_print_state = False

# LLM 인스턴스 생성
llm = ChatOpenAI(model="gpt-4.1-mini")

DB_TUNIVERSE = 'tuniverse_integration_hist_database.db'
TABLE_TUNIVERSE_AFF_HIST = 'aff_if_hist'

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
    result = create_multiline_text(
        "****************   State Info. ****************",
        f"- service_type : {state["service_type"]}",
        f"- user_question : {state["user_question"]}",
        f"- retriever_type : {state["retriever_type"]}",
        f"- embedding_type : {state["embedding_type"]}",
        f"- sql_query : {state["sql_query"]}",
        f"- search_results : {state["search_results"]}",
        "***************   Final Answer  ***************",
        f"{state["final_answer"]}",
        "***********************************************"
    )
    
    return result

def show_state(state: ServiceState):
    print("-"*33, " State Info.  ", "-"*33)
    print("- state.service_type : ", state["service_type"])
    print("- state.user_question : ", state["user_question"])
    print("- state.retriever_type : ", state["retriever_type"])
    print("- state.embedding_type : ", state["embedding_type"])
    print("- state.sql_query : ", state["sql_query"])
    print("- state.search_results : ", state["search_results"])
    print("-"*33, " Final Answer ", "-"*33)
    print(state["final_answer"])
    print("-"*80)