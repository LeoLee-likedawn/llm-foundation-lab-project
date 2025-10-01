from langfuse import get_client
from langfuse.langchain import CallbackHandler
from common import f_print_log

# 콜백 핸들러 생성
langfuse_handler = CallbackHandler()
# Langfuse 클라이언트 초기화
langfuse = get_client()
# 연결 테스트
assert langfuse.auth_check()

def create_prompts_text():
    if f_print_log:
        print("-"*80)
        print("Start create_prompts_text...")
    
    langfuse.create_prompt(
        name="prompt-generate-response-text",  # 프롬프트 이름
        type="text",          
        prompt="""
당신은 사용자 입력에 대해 검색 결과를 참고하여 유용한 답변을 제공하는 전문가입니다.
사용자 입력: {user_question}
검색 결과: {search_results}       
        """,
        labels=["production"],       # 프로덕션 레이블
        tags=["tuniverse", "project", "chat"],    # 태그
        config={
            "model": "gpt-4.1-mini"
        }
    )
    if f_print_log:
        print("--- Create prompt-generate-response-text completed...")

    langfuse.create_prompt(
        name="prompt-check-service-typ-text",  # 프롬프트 이름
        type="text",          
        prompt="""
당신은 사용자 입력을 통해 질문 영역을 판단하고 정해진 답변을 제공하는 전문가입니다.

질문 영역은 "제휴사" 혹은 "채널" 영역이 존재합니다.
다음 제시된 조건에 하나라도 완전히 부합하는 경우 질문 영역을 판단할 수 있습니다.
제시된 조건은 각각 독립적이며 완전히 부합하는 조건이 하나도 없는 경우 질문 영역을 판단할 수 없고 이 경우 "unknown"으로 답변합니다.
제시된 조건은 우선순위의 내림차순이므로 상위 조건 중 완전히 부합하는 조건이 발견되면 하위 조건은 검사하지 않고 영역을 판단하여 답변합니다.
[조건 1-1] 오류코드(400,401,403,404,500과 같은 399보다 크고 600보다 작은 3자리 숫자)가 존재하는 경우 "채널" 영역으로 판단
[조건 1-2] 오류메시지(Access Restricted, Forbidden, Unauthorized, Bad Request, Not Found, Internal Server Error)가 존재하는 경우 "채널" 영역으로 판단
[조건 2-1] 계약번호(3으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 영역으로 판단 
[조건 2-2] 계약서비스번호(6으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 영역으로 판단 
[조건 2-3] 고객(회원)이름(한글2자이상)과 이동전화번호(010으로 시작하는 13자리 숫자), 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 영역으로 판단
[조건 2-4] 고객(회원)번호(1,8,9 로 시작하는 10자리 숫자)와 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 영역으로 판단
                
답변:
"제휴사" 영역이라고 판단되면 "affiliate"로 답변 
"채널" 영역이라고 판단되면 "channel"로 답변
아무 조건도 만족하지 않아 판단이 불가하다면 "unknown"으로 답변

사용자 입력: {user_question}       
        """,
        labels=["production"],       # 프로덕션 레이블
        tags=["tuniverse", "project", "chat"],    # 태그
        config={
            "model": "gpt-4.1-mini"
        }
    )
    if f_print_log:
        print("--- Create prompt-check-service-typ-text completed...")

    langfuse.create_prompt(
        name="prompt-revise-question-text",  # 프롬프트 이름
        type="text",          
        prompt="""
당신은 사용자가 원하는 결과를 응답받을 수 있도록 사용자 입력을 보완하도록 가이드하는 전문가입니다.

사용자 입력의 다음 키워드 포함 여부로 질문 영역을 추측할 수 있습니다.
- 제휴사 영역 : "고객", ""가입", "해지", "변경", "결제"
- 채널 영역 : "오류", "조회"

질문 영역이 "제휴사" 영역이라고 판단되면 다음 조건에 맞는 정보를 사용자가 질문에 추가할 수 있도록 가이드하세요.
[조건 2-1] 계약번호(3으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능
[조건 2-2] 계약서비스번호(6으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능
[조건 2-3] 고객(회원)이름(한글2자이상)과 이동전화번호(010으로 시작하는 13자리 숫자), 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능
[조건 2-4] 고객(회원)번호(1,8,9 로 시작하는 10자리 숫자)와 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능

질문 영역이 "채널" 영역이라고 판단되면 다음 조건에 맞는 정보를 사용자가 질문에 추가할 수 있도록 가이드하세요.
[조건 1-1] 오류코드(400,401,403,404,500과 같은 399보다 크고 600보다 작은 3자리 숫자)가 존재하는 경우 "채널" 영역으로 판단
[조건 1-2] 오류메시지(Access Restricted, Forbidden, Unauthorized, Bad Request, Not Found, Internal Server Error)가 존재하는 경우 "채널" 영역으로 판단

질문 영역을 판단할 수 없다면 질문 영역별로 위 제시된 조건에 맞는 정보를 질문에 추가할 수 있도록 가이드하세요. (제휴사, 채널 영역 분리하여 모두 가이드)

사용자 입력: {user_question}      
        """,
        labels=["production"],       # 프로덕션 레이블
        tags=["tuniverse", "project", "chat"],    # 태그
        config={
            "model": "gpt-4.1-mini"
        }
    )
    if f_print_log:
        print("--- Create prompt-revise-question-text completed...")
        print("-"*80)



def create_prompts_chat():
    if f_print_log:
        print("-"*80)
        print("Start create_prompts_chat...")
    
    langfuse.create_prompt(
        name="prompt-generate-response-chat",  # 프롬프트 이름
        type="chat",          
        prompt=[
            {
                "role": "system",
                "content": """
당신은 사용자 입력에 대해 검색 결과를 참고하여 유용한 답변을 제공하는 전문가입니다.
사용자 입력: {user_question}
검색 결과: {search_results}"""
            },
            {
                "role": "system",
                "content": "다음 정보를 참고하여 답변하세요.\n{{search_results}}"
            },
            {
                "role": "user",
                "content": "{{user_question}}"
            }
        ],
        labels=["production"],       # 프로덕션 레이블
        tags=["tuniverse", "project", "chat"],    # 태그
        config={
            "model": "gpt-4.1-mini"
        }
    )
    if f_print_log:
        print("--- Create prompt-generate-response-chat completed...")

    langfuse.create_prompt(
        name="prompt-check-service-typ-chat",  # 프롬프트 이름
        type="chat",          
        prompt=[
            {
                "role": "system",
                "content": """
당신은 사용자 입력을 통해 질문 영역을 판단하고 정해진 답변을 제공하는 전문가입니다.

질문 영역은 "제휴사" 혹은 "채널" 영역이 존재합니다.
다음 제시된 조건에 하나라도 완전히 부합하는 경우 질문 영역을 판단할 수 있습니다.
제시된 조건은 각각 독립적이며 완전히 부합하는 조건이 하나도 없는 경우 질문 영역을 판단할 수 없고 이 경우 "unknown"으로 답변합니다.
제시된 조건은 우선순위의 내림차순이므로 상위 조건 중 완전히 부합하는 조건이 발견되면 하위 조건은 검사하지 않고 영역을 판단하여 답변합니다.
[조건 1-1] 오류코드(400,401,403,404,500과 같은 399보다 크고 600보다 작은 3자리 숫자)가 존재하는 경우 "채널" 영역으로 판단
[조건 1-2] 오류메시지(Access Restricted, Forbidden, Unauthorized, Bad Request, Not Found, Internal Server Error)가 존재하는 경우 "채널" 영역으로 판단
[조건 2-1] 계약번호(3으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 영역으로 판단 
[조건 2-2] 계약서비스번호(6으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 영역으로 판단 
[조건 2-3] 고객(회원)이름(한글2자이상)과 이동전화번호(010으로 시작하는 13자리 숫자), 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 영역으로 판단
[조건 2-4] 고객(회원)번호(1,8,9 로 시작하는 10자리 숫자)와 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 영역으로 판단
                
답변:
"제휴사" 영역이라고 판단되면 "affiliate"로 답변 
"채널" 영역이라고 판단되면 "channel"로 답변
아무 조건도 만족하지 않아 판단이 불가하다면 "unknown"으로 답변

사용자 입력: {user_question}
            """
            },            
            {
                "role": "user",
                "content": "{{user_question}}"
            }
        ],
        labels=["production"],       # 프로덕션 레이블
        tags=["tuniverse", "project", "chat"],    # 태그
        config={
            "model": "gpt-4.1-mini"
        }
    )
    if f_print_log:
        print("--- Create prompt-check-service-typ-chat completed...")

    langfuse.create_prompt(
        name="prompt-revise-question-chat",  # 프롬프트 이름
        type="chat",          
        prompt=[
            {
                "role": "system",
                "content": """
당신은 사용자가 원하는 결과를 응답받을 수 있도록 사용자 입력을 보완하도록 가이드하는 전문가입니다.

사용자 입력의 다음 키워드 포함 여부로 질문 영역을 추측할 수 있습니다.
- 제휴사 영역 : "고객", ""가입", "해지", "변경", "결제"
- 채널 영역 : "오류", "조회"

질문 영역이 "제휴사" 영역이라고 판단되면 다음 조건에 맞는 정보를 사용자가 질문에 추가할 수 있도록 가이드하세요.
[조건 2-1] 계약번호(3으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능
[조건 2-2] 계약서비스번호(6으로 시작하는 10자리숫자)가 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능
[조건 2-3] 고객(회원)이름(한글2자이상)과 이동전화번호(010으로 시작하는 13자리 숫자), 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능
[조건 2-4] 고객(회원)번호(1,8,9 로 시작하는 10자리 숫자)와 상품명(3자리 이상 문자)이 모두 존재하는 경우 "제휴사" 연동 관련 유용한 답변 가능

질문 영역이 "채널" 영역이라고 판단되면 다음 조건에 맞는 정보를 사용자가 질문에 추가할 수 있도록 가이드하세요.
[조건 1-1] 오류코드(400,401,403,404,500과 같은 399보다 크고 600보다 작은 3자리 숫자)가 존재하는 경우 "채널" 영역으로 판단
[조건 1-2] 오류메시지(Access Restricted, Forbidden, Unauthorized, Bad Request, Not Found, Internal Server Error)가 존재하는 경우 "채널" 영역으로 판단

질문 영역을 판단할 수 없다면 질문 영역별로 위 제시된 조건에 맞는 정보를 질문에 추가할 수 있도록 가이드하세요. (제휴사, 채널 영역 분리하여 모두 가이드)

사용자 입력: {user_question}
                """
            },            
            {
                "role": "user",
                "content": "{{user_question}}"
            }
        ],
        labels=["production"],       # 프로덕션 레이블
        tags=["tuniverse", "project", "chat"],    # 태그
        config={
            "model": "gpt-4.1-mini"
        }
    )
    if f_print_log:
        print("--- Create prompt-revise-question-chat completed...")
        print("-"*80)

# chat 형태의 프롬프트 생성
create_prompts_chat()
# text 형태의 프롬프트 생성
create_prompts_text()