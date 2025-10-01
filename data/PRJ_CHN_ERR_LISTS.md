
## CASE01 - 403/Forbidden
### http 상태 코드
403
### http 상태 메시지
Forbidden
### http 응답 바디
{
  "message" : "Forbidden",
  "status" : 403
}
### 발생원인
API KEY를 누락한 요청
### 해결방안
HTTP 헤더에 “x-api-key” 필드를 추가하고 발급받은 API KEY를 값으로 사용하여 요청 전달하도록 수정
API KEY는 개발자포털에서 생성한 애플리케이션의 “API KEY” 속성 탭을 통해 확인



## CASE02 - 403/Forbidden
### http 상태 코드
403
### http 상태 메시지
Forbidden
### http 응답 바디
{
  "message"" : "Forbidden",
  "status"" : 403
}
### 발생원인
유효하지 않은 API KEY를 이용한 요청
### 해결방안
API KEY는 제휴사마다 발급된 값이 다르고 같은 제휴사라도 환경(STG/PRD)에 따라 값이 상이함
개발자포털에 발급된 API KEY가 정상적으로 요청시 사용되었는지 확인



### CASE03 - 403/Forbidden/Access Restricted
## http 상태 코드
403
## http 상태 메시지
Forbidden
## http 응답 바디
{
  ""message"" : ""Access Restricted"",
  ""status"" : 403
}
## 발생원인
개발자포털에서 "IP/Referer Whitelist" 속성 탭에 서버 IP 미등록 혹은 미등록 서버 IP를 이용한 요청
## 해결방안
개발자포털에서 생성한 애플리케이션의 “IP/Referer Whitelist” 속성 탭에 호출할 서버 IP/Referer 등록
“IP/Referer Whitelist” 속성 탭에 등록된 서버 IP/Referer로 호출이 되었는지 확인



### CASE04 - 403/Forbidden/Access Restricted
## http 상태 코드
403
## http 상태 메시지
Forbidden
## http 응답 바디
{
  ""message"" : ""Access Restricted"",
  ""status"" : 403
}
## 발생원인
개발자포털에 서버 IP와 Referer를  “IP/Referer Whitelist”에 모두 등록
## 해결방안
IP와 Referer가 모두 등록되어 있는 경우 한 쪽만 유효한 것으로 판단하므로 오류 발생 가능
개발자포털에서 생성한 애플리케이션의 “IP/Referer Whitelist” 속성 탭에 IP와 Referer가 모두 등록된 경우 제휴사 정책에 따라 한 쪽은 삭제 필요



### CASE05 - 403/Forbidden
## http 상태 코드
403
## http 상태 메시지
Forbidden
## http 응답 바디
{
  "error"" : "API 접근 권한이 없습니다.",
  "message"" : "접근이 허가되지 않은 API 호출입니다.",
  "timestamp"" : "20241104150507",
  "status"" : 403
}
## 발생원인
HTTP 메소드를 잘못 설정한 상태로 요청
## 해결방안
HTTP 호출시 메소드를 정확하게 세팅하였는지 확인
API마다 서비스 특성에 따라 GET, POST로 메소드가 지정되어 있고 상이한 메소드를 호출하는 경우 오류 발생
개발자포털의 사용 API 목록을 통해 각각의 API에 지정된 메소드를 확인 가능



### CASE06 - 403/Forbidden
## http 상태 코드
403
## http 상태 메시지
Forbidden
## http 응답 바디
{
  "error"" : "API 접근 권한이 없습니다.",
  "message"" : "접근이 허가되지 않은 API 호출입니다.",
  "timestamp"" : "20241104150507",
  "status"" : 403
}
## 발생원인
호출 가능 API에 등록되지 않은 API를 호출
## 해결방안
담당자를 통해 API 등록 여부 확인
이용하고자 하는 서비스에 따라 담당자가 상이할 수 있으므로 담당자를 모르는 경우 별도 문의 필요



### CASE07 - 401/Unauthorized
## http 상태 코드
401
## http 상태 메시지
Unauthorized
## http 응답 바디
{ 
   "error": "token not authorized", 
   "message": "token not authorized", 
   "timestamp": "20241105102919", 
   "status"": 401
}
## 발생원인
대고객용 채널 API 호출시 HTTP 헤더에 CI를 누락하고 요청
## 해결방안
HTTP 헤더에 “x-cnnt-info” 필드를 추가하고 고객의 CI를 세팅하여 요청 전달하도록 수정



### CASE08 - 500/Internal Server Error
## http 상태 코드
500
## http 상태 메시지
Internal Server Error
## http 응답 바디
{
    "timestamp": ""20241205175222",
    "status"": 500,
    "code"": "COM_9999"",
    "message"": "[COM_9999] 내부 오류가 발생하였습니다"
}
## 발생원인
전문 구성 오류
## 해결방안
요청 바디의 구성에 오류가 있거나 바디의 구성이 사전 정의된 것과 다르게 구성된 경우 발생 가능
요청 전문의 구조(JSON)가 정상인지 확인
이중따움표 누락이나 잘못된 위치에 배치하는 경우 빈번하게 발생



### CASE09 - 400/Bad Request
## http 상태 코드
400
## http 상태 메시지
Bad Request
## http 응답 바디
{
    ""timestamp"": ""20241205175035"",
    ""status"": 400,
    ""code"": ""ORD_MSG_003"",
    ""message"": ""r3kPrdId은 자리수가 8 자리입니다.""
}
## 발생원인
파라미터 값 오류
## 해결방안
파라미터의 형식이나 자리 수가 맞지 않는 경우 발생 가능
요청된 전문의 파라미터(값)가 정상인지 확인



### CASE10 - 400/Bad Request
## http 상태 코드
400
## http 상태 메시지
Bad Request
## http 응답 바디
{
    ""error"": ""CI-URL FeignException"",
    ""message"": ""No content to map due to end-of-input\n at. [Source: (String)\""\""; line: 1, column: 0]"",
    ""timestamp"": ""2024-12-11T17:36:52.608395631"",
    ""status"": 400
}
## 발생원인
대고객용 채널 API 호출시 HTTP 헤더에 첨부된 CI에 해당하는 고객이 존재하지 않는 경우 발생
## 해결방안
T우주 고객으로 먼저 등록하도록 유도하고 고객 등록이 완료된 후에 다시 호출 필요
고객 등록이 필요하지 않은 경우 정보가 없는 것으로 판단하고 자체적으로 후속 프로세스 진행 필요
