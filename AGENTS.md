# AGENTS.md — 업무 말투 변환기 (BizTalk) 개발 지침서

이 문서는 **업무 말투 변환기** 프로젝트를 개발할 때 **Google Antigravity(AI 에이전트)**가 반드시 준수해야 하는 행동 규칙, 프로젝트 개요, 아키텍처 및 작업 절차를 정의합니다.

---

## 1. 프로젝트 개요 (Project Overview)

- **프로젝트명**: 업무 말투 변환기 (biztalk_antigravity)
- **목적**: 사용자가 편하게 입력한 일상적 문장을 비즈니스 상황과 수신 대상(상사, 타팀 동료, 고객, 팀내 동료)에 적합한 정중한 비즈니스 말투로 자동 변환하는 서비스
- **목표 지향점**: "완벽한 서비스"가 아니라 명세에 맞게 **"작동하는 최소 기능 서비스(MVP)"**를 완성도 높게 구현하는 One Day 바이브 코딩(Vibe Coding) 프로젝트
- **실습 범위**:
  - ✅ **포함**: 텍스트 입력창, 수신 대상 선택(4종), FastAPI + Upstage Solar-Pro4 기반 말투 변환 API, 결과 출력 및 클립보드 복사, Vercel 배포
  - ❌ **제외 (오버엔지니어링 금지)**: 로그인/인증, DB 기반 변환 이력 저장, 복잡한 재시도 로직, 불필요한 프레임워크 도입

---

## 2. 기술 스택 (Technology Stack)

| 영역 | 기술 스택 | 설명 / 비고 |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+, FastAPI, Uvicorn | 경량 REST API 서버, Swagger UI (`/docs`) 지원 |
| **LLM & Agent** | Upstage Solar-Pro4, LangChain, `langchain-upstage` | 한국어 비즈니스 문맥 특화 LLM 연동 |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+) | 빌드 도구 없는 순수 웹 표준 (No React/Vue) |
| **환경 변수** | `python-dotenv` | `.env` 파일을 통한 `UPSTAGE_API_KEY` 관리 |
| **배포/호스팅** | GitHub, Vercel | 프론트엔드 및 서버리스 백엔드 배포 |
| **도구/MCP** | Context7, Playwright, GitHub MCP | 라이브러리 최신 문서 확인, 브라우저 E2E 테스트용 |

---

## 3. 프로젝트 디렉토리 구조 (Directory Structure)

에이전트는 코드 작성 시 PRD에 정의된 디렉토리 구조를 엄격히 준수해야 합니다.

```text
biztalk_antigravity/
├── .agents/                    # 에이전트 스킬 및 MCP 설정
│   ├── Skills/
│   │   ├── frontend-design/    # UI/UX 디자인 가이드라인
│   │   └── karpathy-guidelines/# Karpathy 코딩 원칙
│   └── mcp_config.json         # GitHub, Context7, Playwright MCP
├── .venv/                      # Python 가상환경 (Git 제외)
├── backend/
│   ├── main.py                 # FastAPI 앱 엔트리포인트, CORS, 정적 라우팅
│   ├── routers/
│   │   └── convert.py          # POST /api/convert 라우터
│   ├── services/
│   │   └── tone_converter.py   # LangChain + Solar-Pro4 연동 비즈니스 로직
│   ├── prompts/
│   │   └── templates.py        # 수신 대상별 프롬프트 템플릿
│   ├── models/
│   │   └── schemas.py          # Pydantic 요청/응답 스키마
│   └── requirements.txt        # 의존성 패키지 목록
├── frontend/
│   ├── index.html              # 메인 웹 페이지
│   ├── css/
│   │   └── style.css           # UI 스타일
│   └── js/
│       └── app.js              # DOM 조작, API 비동기 호출 (Fetch API)
├── .env                        # Upstage API 키 (보안 주의: 커밋/노출 절대 금지)
├── .gitignore                  # Git 추적 제외 목록
├── AGENTS.md                   # 본 에이전트 지침서
├── PRD_업무말투변환기.md            # 제품 요구사항 명세서
└── 개요서_업무말투변환기.md          # 프로그램 개요서
```

---

## 4. API 명세 (API Specifications)

### 4.1. `POST /api/convert` (핵심 변환 API)
- **Request Body**:
  ```json
  {
    "text": "내일까지 보고서 제출 어려울 것 같음",
    "target_audience": "boss"
  }
  ```
  - `text` (string, 필수): 변환할 원문 (1자 이상)
  - `target_audience` (string, 필수): `boss` | `colleague` | `client` | `team`
- **Response Body (200 OK)**:
  ```json
  {
    "converted_text": "안녕하세요. 보고서 제출 일정과 관련하여 말씀드립니다...",
    "target_audience": "boss",
    "original_text": "내일까지 보고서 제출 어려울 것 같음"
  }
  ```
- **Error Codes**:
  - `422 Unprocessable Entity`: 입력값 유효성 검증 실패
  - `500 Internal Server Error`: LLM API 호출 또는 서버 내부 오류

### 4.2. `GET /health` (상태 확인)
- **Response (200 OK)**: `{"status": "ok"}`

### 4.3. `GET /docs` (Swagger UI)
- 대화형 API 문서 및 즉시 테스트 제공

---

## 5. 수신 대상별 프롬프트 전략 (Prompt Matrix)

| 코드 (`target_audience`) | 대상 | 어조 및 페르소나 |
| :--- | :--- | :--- |
| `boss` | 상사 / 임원 | 격식 있는 경어체, 공손하고 결론 중심의 명확한 문장 |
| `colleague` | 타팀 동료 | 정중하되 상호 존중과 협조를 구하는 깔끔한 업무 어조 |
| `client` | 고객 / 외부 | 친절하고 신뢰감을 주는 서비스 응대 어조, 사려 깊은 배려 |
| `team` | 팀 내 동료 | 불필요한 미사여구를 줄이고 신속하고 실무적인 간결한 어조 |

---

## 6. Antigravity 에이전트 필수 준수 규칙 (Agent Rules)

### 6.1. 바이브 코딩 3대 원칙 (PRD 기반)
1. **완료 기준을 먼저 정의하라 (Simplicity & Scope)**
   - PRD의 완료 체크리스트 항목만 구현하며, 요청받지 않은 기능(인증, DB, 복잡한 통계 등)을 임의로 추가하지 않습니다.
   - 단일 목적 함수에 불필요한 계층 분리나 추상화를 도입하지 않습니다.
2. **조사 먼저, 구현 나중 (Investigate First, Code Later)**
   - 외부 라이브러리(`langchain-upstage`, Upstage Solar-Pro4)를 사용할 때는 사전에 모델명, 초기화 방식, 의존성 호환성을 먼저 확인한 뒤 코드를 작성합니다.
   - 추측에 의존하지 않고 Context7 또는 공식 가이드를 참조합니다.
3. **버그는 분석 먼저, 수정 나중 (Analyze Root Cause First)**
   - 오류 발생 시 맹목적으로 코드를 덮어쓰거나 누더기 코드를 만들지 않습니다.
   - 오류 원인(원인 파악)을 사용자에게 명확히 설명하고 승인된 방향으로 최소 단위의 외과수술적 수정을 진행합니다.

### 6.2. Karpathy 코딩 원칙 (Karpathy Guidelines)
- **Think Before Coding**: 불분명한 요구사항은 가정을 세워 멋대로 처리하지 않고 먼저 질문하여 명확히 합니다.
- **Minimum Code**: 코드량이 적을수록 버그가 적습니다. 50줄로 끝낼 수 있는 로직을 200줄로 과도하게 작성하지 마십시오.
- **Surgical Changes**: 수정 시 영향 범위를 최소화합니다. 요청받은 부분 외에 인접한 정상 코드를 임의로 리팩토링하거나 건드리지 않습니다.
- **Goal-Driven Execution**: 매 단계마다 검증 기준(동작 테스트, 서버 기동, API 호출 테스트)을 세우고 이를 확인한 후 다음 단계로 진행합니다.

### 6.3. 보안 및 안전 관리 원칙 (Global Safety Policy)
- 🚫 **`.env` 파일 내용 출력 및 변경 절대 금지**: API 키, 민감 정보가 포함된 파일의 내용을 터미널이나 응답에 노출하지 않습니다.
- 🚫 **파괴적 Git 명령어 금지**: `git push --force`, `git reset --hard`, `git clean -fd` 등 히스토리를 유실시키는 명령을 실행하지 않습니다.
- ⚠️ **사전 확인 원칙**: 패키지 설치(`pip install`), 새 파일 생성, 중요 아키텍처 변경 시 사용자에게 사전에 안내합니다.

---

## 7. 단계별 개발 가이드 (Roadmap)

### STEP 1. 환경 준비 및 검증
- [x] `.gitignore` 보강 (`.venv/`, `__pycache__/`, `*.pyc`, `.env` 등)
- [x] `backend/requirements.txt` 작성 (`fastapi`, `uvicorn`, `langchain`, `langchain-upstage`, `python-dotenv`, `pydantic`)
- [x] Python 가상환경(`.venv`) 준비 및 패키지 설치
- [x] Upstage API 연동 테스트 환경 검증

### STEP 2. 백엔드 구현 (FastAPI + Upstage)
- [x] `backend/models/schemas.py`: Pydantic 요청/응답 스키마 정의
- [x] `backend/prompts/templates.py`: 대상별 시스템/유저 프롬프트 작성
- [x] `backend/services/tone_converter.py`: ChatUpstage (Solar-Pro) 호출 파이프라인
- [x] `backend/routers/convert.py`: API 라우터 구현 및 예외 처리
- [x] `backend/main.py`: CORS 설정, 헬스체크(`/health`), 정적 파일 마운트
- [x] Swagger UI (`http://localhost:8000/docs`) 로컬 테스트 검증

### STEP 3. 프론트엔드 구현 (Vanilla HTML/CSS/JS)
- [x] `frontend/index.html`: 시맨틱 마크업, 텍스트 입력창, 4종 대상 선택 버튼, 결과 영역, 복사 버튼
- [x] `frontend/css/style.css`: 모던하고 깔끔한 비즈니스 감성의 UI 스타일링 (디자인 스킬 참조)
- [x] `frontend/js/app.js`: 이벤트 리스너, 로딩 인디케이터 처리, Fetch API 연동, 클립보드 복사 API
- [x] 브라우저 환경에서 실제 E2E 연동 테스트

### STEP 4. 배포 준비
- [x] GitHub 저장소 커밋 전 `.env` 누락 여부 확인
- [x] Vercel 배포 설정 (`vercel.json` 등 필요 시 구성)
- [x] Vercel CLI 원클릭 자동 배포 스크립트 (`deploy.ps1`, `deploy.bat`, `package.json`) 작성 완료
- [x] GitHub 원격 저장소(`origin/main`) 푸시 완료
- [ ] Vercel 배포 및 원격 환경 동작 검증
------
### 5. @PRD_업무말투변환기.md 문서와 AGENTS.md 문서 항상 최신화 하기
* 모든 변경사항이 발생하면 (예를 들어 기능이나 요구사항이 변경 되거나, 화면명세가 변경되거나, Source Code가 변경 되거나 라이브러리 버전이 변경되면) 관련된 markdown 문서들도 반드시 업데이트 합니다. 
* 구현이 완료된 사항들은 `@PRD_업무말투변환기.md\2. 완료 체크리스트`에 모두 체크표시를 해서 완료 되었음을 반드시 표시하세요.
* `@PRD_업무말투변환기.md\8. 단계별 구현 순서` 에서도 단계별로 구현이 완료되면 체크표시를 해서 완료 되었음을 반드시 표시하세요.
