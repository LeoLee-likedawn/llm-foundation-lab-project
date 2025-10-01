from common import ServiceState, show_state, merge_state, f_print_state
from service_channel_qna import chn_svc_qna
from service_affiliate_qna import aff_svc_qna
from service_generate_response import gen_res
from service_revise_qna import revise_qna
from service_check_service_type import chk_svc_typ, decide_next_step

from langgraph.graph import StateGraph, START, END

# 그래프 구성
builder = StateGraph(ServiceState)

# 노드 추가: 입력 분석, 한국어 문서 검색, 영어 문서 검색, 답변 생성
builder.add_node("chk_svc_typ", chk_svc_typ)
builder.add_node("aff_svc_qna", aff_svc_qna)
builder.add_node("chn_svc_qna", chn_svc_qna)
builder.add_node("revise_qna", revise_qna)
builder.add_node("gen_res", gen_res)

# 엣지 추가: 시작 -> 사용자 입력 분석 -> 조건부 엣지 -> 한국어 문서 검색 또는 영어 문서 검색 -> 답변 생성 -> 끝
builder.add_edge(START, "chk_svc_typ")

# 조건부 엣지 추가
builder.add_conditional_edges(
    "chk_svc_typ",
    decide_next_step
)

builder.add_edge("aff_svc_qna", "gen_res")
builder.add_edge("chn_svc_qna", "gen_res")
builder.add_edge("revise_qna", END)
builder.add_edge("gen_res", END)

# 그래프 컴파일
graph = builder.compile()

# 그래프 시각화
#display(Image(graph.get_graph().draw_mermaid_png()))

def call_my_service(message, history):

    history = history or []
    
    init_state = ServiceState(
        user_question=message,
        #user_question="카리나 고객의 스타벅스와 관련된 연동 이력을 확인해주세요.",
        #user_question="채널 연동중 ""Access Restricted"" 메시지와 함께 오류가 발생하는데 원인은 무엇인가요?",
        #user_question="채널 연동중 ""Access Restricted"" 메시지와 함께 오류가 발생하는데 원인은 무엇인가요?",
        #user_question="""채널 연동중 "message" : "Access Restricted"이 포함된 메시지와 함께 오류가 발생하는데 원인은 무엇인가요?""",
        #user_question="500 오류가 발생하였는데 조치할 방안이 있나요?",
        sql_query="",
        service_type="",
        need_to_revise=False,
        retriever_type="S", # S : similarity, M : mmr, T : threshold
        embedding_type="ollama", # ollama, openai
        search_results=[],
        final_answer=""
    )

    # 그래프 실행
    result = graph.invoke(init_state)

    show_state(result)

    response = result['final_answer']

    if f_print_state:
        response = merge_state(result)
    
    history.append((message, response))
    
    # 결과 출력
    #return result['final_answer']
    return history, history