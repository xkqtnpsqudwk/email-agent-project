# Multi-Agent Email Processing System

> This project implements a multi-agent email processing system using parallel execution and tool/function calling. Each agent processes emails independently, classifies them into predefined categories, and calls appropriate tools such as spam detection, schedule conflict checking, auto-reply saving, and report generation.

---

## 과제 개요 (Assignment Overview)

이 프로젝트는 EPITECH 수업 과제로, **멀티 AI 에이전트 이메일 처리 시스템**을 구현합니다.

여러 개의 이메일을 여러 에이전트가 병렬로 처리하고, 각 이메일을 5가지 카테고리로 분류한 후 Tool / Function Calling 방식으로 필요한 액션을 수행합니다. LLM API 없이 **규칙 기반 분류기(rule-based classifier)**로 구현되었으며, 실제 AI 에이전트 구조를 시뮬레이션합니다.

---

## 주요 기능 (Key Features)

- **Multi-Agent**: 이메일마다 독립적인 에이전트가 할당되어 병렬 처리
- **병렬 처리**: `concurrent.futures.ThreadPoolExecutor`로 동시 실행
- **Tool Calling**: 에이전트가 상황에 따라 tool 함수를 선택적으로 호출
- **5가지 이메일 분류**: spam, no_response_needed, decision_required, notification_only, auto_reply_possible
- **스케줄 충돌 감지**: 이메일 내 시간 정보와 기존 일정 비교
- **자동 답장 저장**: 답장 가능한 이메일에 자동 답장 생성 및 저장
- **스팸 발신자 등록**: 신규 스팸 발신자를 자동으로 목록에 추가

---

## 프로젝트 구조 (Project Structure)

```
email_agent_project/
├── main.py                  # 진입점: 이메일 로드, 에이전트 생성, 병렬 실행, 리포트 출력
├── config.py                # 이메일 소스 설정 (dummy / gmail 전환)
├── agents/
│   ├── __init__.py
│   └── email_agent.py       # EmailAgent 클래스: 분류 + tool 호출 로직
├── tools/
│   ├── __init__.py
│   ├── file_lock.py         # 스레드 안전 파일 I/O를 위한 공유 Lock
│   ├── email_tools.py       # load_emails_tool (소스 라우팅), normalize_email_tool
│   ├── gmail_tools.py       # Gmail API 연동 (load_emails_from_gmail)
│   ├── spam_tools.py        # check_spam_sender_tool, add_spam_sender_tool
│   ├── schedule_tools.py    # check_schedule_conflict_tool
│   ├── reply_tools.py       # save_sent_reply_tool
│   └── report_tools.py      # save_report_tool
├── data/
│   ├── dummy_mails.json     # 더미 수신 이메일 목록
│   ├── spam_senders.json    # 스팸 발신자 목록 (실행 후 업데이트됨)
│   ├── schedule.json        # 기존 일정 목록
│   ├── sent_mails.json      # 자동 답장 저장 (실행 시 초기화)
│   └── report.json          # 처리 결과 저장 (실행 시 초기화)
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 실행 방법 (How to Run)

### 요구 사항

- Python 3.7 이상
- 외부 라이브러리 불필요 (표준 라이브러리만 사용)

### 실행 명령어

```bash
# 프로젝트 디렉토리로 이동
cd email_agent_project

# 실행
python main.py
```

> **참고**: `spam_senders.json`은 실행 후 신규 스팸 발신자가 추가됩니다. 초기 상태로 되돌리려면 파일을 `["known_spam@example.com", "promo@spamsite.com"]`으로 리셋하세요.

---

## 예시 실행 결과 (Sample Output)

```
[System] Resetting output files...
[System] Loading emails...
[System] 8 emails loaded. Starting parallel processing...

[Agent-1] call tool: normalize_email_tool
[Agent-1] call tool: check_spam_sender_tool
[Agent-3] call tool: normalize_email_tool
[Agent-3] call tool: check_spam_sender_tool
[Agent-2] call tool: normalize_email_tool
[Agent-2] call tool: check_spam_sender_tool
[Agent-1] call tool: save_report_tool
[Agent-3] call tool: check_schedule_conflict_tool
[Agent-2] call tool: add_spam_sender_tool
[Agent-2] call tool: save_report_tool
[Agent-3] call tool: save_report_tool
...

=======================================================
           EMAIL PROCESSING REPORT
=======================================================

[Decision Required]
  - 일정 충돌: project.manager@example.com의 회의 요청이 기존 일정과 충돌합니다.
  - 의사결정 필요: finance@example.com의 메일은 사용자의 선택이 필요합니다.

[Auto Replied]
  - alice@example.com에게 자동 답장을 저장했습니다.
  - hr@example.com에게 자동 답장을 저장했습니다.

[Notification Only]
  - server@example.com의 Server Maintenance Completed 메일을 확인했습니다.

[No Response Needed]
  - newsletter@example.com의 메일은 응답이 필요 없습니다.

[Spam]
  - known_spam@example.com은 기존 스팸 발신자입니다.
  - new_scam@example.com을 신규 스팸 발신자로 등록했습니다.

=======================================================
  Total processed: 8 emails
=======================================================
```

> 병렬 처리로 인해 tool 호출 로그의 순서는 실행마다 달라질 수 있습니다.

---

## Multi-Agent 구현 설명

`main.py`에서 이메일 개수만큼 `EmailAgent` 인스턴스를 생성합니다.

```python
agents = [EmailAgent(f"Agent-{i + 1}") for i in range(len(emails))]
```

각 에이전트는 고유한 `agent_id`를 가지며, 서로 다른 이메일을 독립적으로 처리합니다. 에이전트들은 상태를 공유하지 않으므로 진정한 멀티 에이전트 구조를 구현합니다.

---

## 병렬 처리 구현 설명

`concurrent.futures.ThreadPoolExecutor`를 사용하여 에이전트들이 동시에 실행됩니다.

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        executor.submit(agent.process_email, email): agent.agent_id
        for agent, email in zip(agents, emails)
    }
    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())
```

- `max_workers=4`: 최대 4개의 스레드가 동시에 실행
- `as_completed()`: 완료되는 순서대로 결과를 수집
- 파일 쓰기 충돌 방지를 위해 `tools/file_lock.py`의 `threading.Lock()` 사용

---

## Tool / Function Calling 구현 설명

각 에이전트는 직접 로직을 구현하지 않고, 상황에 따라 tool 함수를 선택적으로 호출합니다.

| Tool 함수 | 파일 | 역할 |
|---|---|---|
| `load_emails_tool` | email_tools.py | 이메일 파일 로드 |
| `normalize_email_tool` | email_tools.py | 이메일 정규화 |
| `check_spam_sender_tool` | spam_tools.py | 스팸 발신자 확인 |
| `add_spam_sender_tool` | spam_tools.py | 신규 스팸 등록 |
| `check_schedule_conflict_tool` | schedule_tools.py | 일정 충돌 확인 |
| `save_sent_reply_tool` | reply_tools.py | 자동 답장 저장 |
| `save_report_tool` | report_tools.py | 처리 결과 저장 |

에이전트가 tool을 호출할 때마다 콘솔에 로그가 출력됩니다:

```
[Agent-1] call tool: check_spam_sender_tool
[Agent-1] call tool: save_report_tool
```

---

## 사용한 데이터 파일 설명

| 파일 | 설명 | 동작 |
|---|---|---|
| `dummy_mails.json` | 처리할 더미 수신 이메일 8개 | 읽기 전용 |
| `spam_senders.json` | 알려진 스팸 발신자 목록 | 신규 스팸 발신자 추가됨 |
| `schedule.json` | 기존 일정 목록 (충돌 감지용) | 읽기 전용 |
| `sent_mails.json` | 자동 답장 저장소 | 실행 시 초기화 후 추가됨 |
| `report.json` | 최종 처리 결과 저장소 | 실행 시 초기화 후 추가됨 |

---

## Gmail API로 확장하는 방법

**이 프로젝트는 Gmail API 확장이 이미 구현되어 있습니다.** 더미 모드와 Gmail 모드를 `config.py` 한 줄로 전환할 수 있도록 설계했습니다.

### 동작 구조

```
config.EMAIL_SOURCE = "dummy"   →  data/dummy_mails.json 읽기 (기본값, API 키 불필요)
config.EMAIL_SOURCE = "gmail"   →  tools/gmail_tools.py 로 실제 Gmail 읽기
```

`tools/email_tools.py`의 `load_emails_tool()`이 설정값에 따라 소스를 라우팅합니다:

```python
def load_emails_tool():
    if config.EMAIL_SOURCE == 'gmail':
        from tools.gmail_tools import load_emails_from_gmail
        return load_emails_from_gmail()
    return _load_emails_from_dummy()
```

`tools/gmail_tools.py`가 Gmail API로 받은 메일을 **더미 데이터와 동일한 딕셔너리 형식**(`{id, from, subject, body, start_time, end_time}`)으로 변환하므로, **에이전트 로직과 나머지 tool 함수는 전혀 변경할 필요가 없습니다.**

### 실제 Gmail 연동 활성화 방법

> 아래 단계는 실제 Gmail 계정에 연결할 때만 필요합니다. API 키 없이도 더미 모드로 프로젝트는 정상 동작합니다.

1. 필요한 패키지 설치:
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```
2. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성 후 **Gmail API** 활성화
3. **OAuth 2.0 클라이언트 ID**(Desktop app) 생성 후 자격증명 다운로드 → `data/credentials.json`으로 저장
4. `config.py`에서 `EMAIL_SOURCE = "gmail"`로 변경
5. `python main.py` 실행 → 브라우저 로그인 창이 열리고, 인증 토큰이 `data/token.json`에 자동 저장됨

> `credentials.json`과 `token.json`은 민감 정보이므로 `.gitignore`에 이미 포함되어 GitHub에 올라가지 않습니다.

---

## GitHub에 업로드하는 방법

```bash
git init
git add .
git commit -m "Initial commit: multi-agent email processing system"
git branch -M main
git remote add origin https://github.com/USERNAME/REPOSITORY_NAME.git
git push -u origin main
```

> **주의**: `USERNAME`은 본인의 GitHub 사용자명으로, `REPOSITORY_NAME`은 생성한 리포지토리 이름으로 직접 변경해야 합니다.
