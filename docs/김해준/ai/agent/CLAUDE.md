# CLAUDE.md — synapse-platform-svc

> 이 파일은 Claude Code 세션 시작 시 자동으로 로드됩니다.
> Agent는 아래 순서대로 컨텍스트를 파악한 뒤 작업을 시작하세요.

---

## 1. 프로젝트 한 줄 정의

**Synapse** — 노트 → 플래시카드 자동 생성 → AI 간격 반복 학습 SaaS (PKM + SRS + AI 통합)

이 서비스(`synapse-platform-svc`)는 MSA를 구성하는 4개 백엔드 서비스 중 하나로,
**인증 허브 역할**을 담당합니다. 전체 MSA의 JWT 검증 의존성 기점입니다.

```
Gateway → synapse-platform-svc (인증 허브)
              ├── auth        OAuth 2.0 (Google/GitHub) / JWT / MFA (TOTP)
              ├── user        사용자 프로필 관리
              ├── notification FCM 푸시 + AWS SES 이메일
              └── admin       관리자 기능 / Audit Log / Kafka Consumer
```

- **담당자**: 김해준 (트랙 A, 1인 전담)
- **GitHub**: `team-project-final/synapse-platform-svc`
- **기간**: 2026-05-12 ~ 2026-06-15 (5주 + 발표일)

---

## 2. 세션 시작 시 필수 확인 (순서 준수)

새 세션이 시작될 때마다 아래 순서대로 읽어 현재 위치를 파악하세요.

```
── AI 현재 상태 (먼저 확인) ──────────────────────────────────

1. docs/ai/current/TASK.md
   → 현재 진행 중인 Step + Phase + Done When 확인

2. docs/ai/current/CONTEXT.md
   → 확정된 것 / 미결 사항 / 활성 제약 확인

── 공식 프로젝트 문서 (보완 확인) ───────────────────────────

3. docs/project-management/task/TASK_platform.md
   → 현재 Step Done When 기준 + 전체 로드맵 파악

4. docs/project-management/workflow/WORKFLOW_platform_W{현재주차}.md
   → 10단계 체크리스트 현황 확인

5. docs/project-management/history/HISTORY_platform.md
   → 마지막 작업일 기록 확인
```

> docs/ai/current/TASK.md가 비어 있으면 TASK_platform.md에서 다음 Step을 찾아 채웁니다.

현재 주차는 오늘 날짜 기준으로 판단합니다:
- W1: 05-12 ~ 05-16
- W2: 05-19 ~ 05-23
- W3: 05-26 ~ 05-29
- W4: 06-01 ~ 06-05

---

## 3. docs 폴더 구조

```
docs/
├── project-management/          ← 공식 프로젝트 문서 (팀 공유, 수정 시 PR 필요)
│   ├── KICKOFF.md              프로젝트 전체 개요 + 팀 구성 + CI/CD + Git 규칙
│   ├── scope/
│   │   └── SCOPE_platform.md   4주 전체 책임 범위 (In/Out of Scope)
│   ├── prd/
│   │   ├── PRD_W1.md           Week 1 기능 요구사항 + 수용 기준
│   │   ├── PRD_W2.md           Week 2 기능 요구사항 + 수용 기준
│   │   ├── PRD_W3.md           Week 3 기능 요구사항 + 수용 기준
│   │   └── PRD_W4.md           Week 4 기능 요구사항 + 수용 기준
│   ├── task/
│   │   └── TASK_platform.md    Step별 작업 정의 (Goal / Done When / Instructions)
│   ├── workflow/
│   │   ├── WORKFLOW_platform_W1.md   W1 Step별 10단계 체크리스트
│   │   ├── WORKFLOW_platform_W2.md
│   │   ├── WORKFLOW_platform_W3.md
│   │   └── WORKFLOW_platform_W4.md
│   └── history/
│       └── HISTORY_platform.md  날짜별 작업 일지
├── rules/                       ← 코딩 룰북 (17개 파일) — 작업 전 반드시 참조
│   ├── 01-security.md
│   ├── 02-function.md
│   ├── 03-technical.md
│   ├── 04-quality.md
│   ├── 05-operation.md
│   ├── 06-auth-token.md        JWT/OAuth 관련 규칙
│   ├── 07-platform-spring.md   Spring 관련 규칙
│   ├── 07-platform.md
│   ├── 08-kafka-event.md       Kafka 이벤트 규칙
│   ├── 09-observability.md
│   ├── 10-container-k8s.md
│   ├── 11-data-sovereignty.md
│   ├── 12-working-log.md
│   ├── 14-task-structure.md
│   ├── appendix-a-asvs.md
│   ├── appendix-b-owasp.md
│   └── appendix-c-checklist.md
├── spike/                       ← 기술 검증 문서 보관 (검증 계획 + 결과 정리)
│   └── {기능명}/               스파이크 목표 + 결과 문서
└── ai/                          ← AI Agent 전용 문서 (공식 문서와 분리)
    ├── agent/                   Agent별 고정 지침 (태스크마다 바뀌지 않음)
    │   ├── director.md          Claude — 설계 판단 / 작업 분해 / 코드 리뷰
    │   ├── worker.md            Codex — 코드 작성 / 테스트 / 리팩토링
    │   └── researcher.md        Gemini — 기술 조사 / 공식 문서 / 비교 분석
    ├── current/                 현재 태스크 상태 (단일 source of truth)
    │   ├── TASK.md              현재 Step 실제 작업 내용 (TASK_platform에서 복사)
    │   ├── CONTEXT.md           현재 판단 가능한 상태 (확정/미결/제약)
    │   └── HANDOFF.md           Agent 간 전달 문서
    ├── templates/               current/ 파일 초기화용 빈 템플릿
    │   ├── TASK.md
    │   ├── CONTEXT.md
    │   └── HANDOFF.md
    ├── decisions/
    │   └── DECISION_LOG.md      설계 결정 이력 (append-only)
    └── archive/                 완료된 태스크 스냅샷
        └── {YYYYMMDD}-{step}/
```

---

## 4. AI Agent 워크플로

### Agent 역할 분담

| Agent | 역할 | 지침 파일 |
|-------|------|----------|
| Director (Claude) | 설계 판단 / 작업 분해 / 코드 리뷰 / 아키텍처 결정 | docs/ai/agent/director.md |
| Worker (Codex) | 코드 작성 / 테스트 / 리팩토링 / 반복 작업 | docs/ai/agent/worker.md |
| Researcher (Gemini) | 기술 조사 / 공식 문서 / 비교 분석 | docs/ai/agent/researcher.md |

> AI 간 직접 대화 없음. 모든 상태 공유는 docs/ai/current/ 문서를 통해 진행합니다.

### 태스크 생명주기

```
[시작]
  1. TASK_platform.md에서 다음 Step 확인
  2. docs/ai/current/TASK.md 채우기 (Done When 복사)
  3. docs/ai/current/CONTEXT.md 초기화
  4. TASK_platform.md Status → In Progress

[진행]
  5. 조사 필요 시 → HANDOFF.md 작성 (TO: Researcher)
  6. 구현 필요 시 → HANDOFF.md 작성 (TO: Worker)
  7. 설계 결정 발생 시 → DECISION_LOG.md 추가
  8. Agent 결과 수신 후 → CONTEXT.md 갱신

[완료]
  9. current/ 전체를 archive/{YYYYMMDD}-{step}/ 로 이동
  10. current/ 파일 초기화 (templates/에서 복사)
  11. TASK_platform.md Status → Done
  12. WORKFLOW 체크리스트 전체 체크
  13. HISTORY_platform.md 완료일 기록
```

### Agent에게 건넬 때 첨부 원칙

```
Director (Claude)   → CLAUDE.md + current/TASK.md + current/CONTEXT.md
Worker (Codex)      → agent/worker.md + current/HANDOFF.md + current/CONTEXT.md
Researcher (Gemini) → agent/researcher.md + current/HANDOFF.md
```

최소한의 파일만 첨부합니다. 관련 없는 파일은 컨텍스트 낭비입니다.

---

## 5. 10단계 개발 워크플로

각 Step을 실행할 때 반드시 이 순서로 진행합니다. WORKFLOW 파일의 체크박스와 연동됩니다.

```
① TASK 확인          Goal / Done When / Scope / Input 읽기
② 요구사항 분석       Instructions 정리 + 관련 PRD 확인
③ Security 1차       인증 필요? 권한 종류? 공개 API?
④ ERD 설계           테이블 설계 + 인덱스 + 관계 정의
⑤ Security 2차       암호화? Soft Delete? 행단위 접근?
⑥ DTO/Entity 설계    API First: DTO 먼저 → Entity 나중
⑦ Repository 구현
⑧ Service + Test     동시에 작성
⑨ Controller + Test  동시에 작성 (401/403 포함)
⑩ View + Test        Smoke 1건 이상 필수
```

**Step 시작 시**: `TASK_platform.md`의 해당 Step Status → `In Progress` 갱신 + HISTORY에 시작일 기록
**Step 완료 시**: Status → `Done` + WORKFLOW 전체 체크 + HISTORY에 완료일 기록

---

## 6. TASK 로드맵 — 실제 작업 흐름

> `docs/project-management/task/TASK_platform.md` — 모든 구현 작업의 단일 기준점

### 역할

- **무엇을** / **언제까지** / **어떻게** 구현할지를 Step 단위로 정의합니다
- Done When이 충족되지 않으면 Step 완료가 아닙니다
- Step 순서는 의존성 기반이므로 **순서 변경 금지**

### Step 구조

각 Step은 다음 항목으로 구성됩니다:

```
Step Goal     — 이 Step이 끝났을 때 달성되는 상태 (한 문장)
Done When     — 완료 판단 기준 체크리스트 (모두 충족 필수)
Scope         — In Scope / Out of Scope 명확히 구분
Instructions  — 구현 순서 (1번부터 순서대로 진행)
Constraints   — 이 Step에만 적용되는 제약사항
Duration      — 예상 소요 시간
Status        — Not Started / In Progress / Done
```

### 전체 Step 현황

| Step | 목표 | 주차 | 상태 |
|------|------|------|------|
| Step 1 | platform-svc 골격 생성 | W1 | ✅ Done |
| Step 2 | Google/GitHub OAuth 회원가입/로그인 | W1 | ✅ Done |
| Step 3 | JWT Access/Refresh Token + MFA(TOTP) | W1 | ✅ Done |
| Step 4 | Stripe Checkout 결제 + Webhook | W2 | ⬜ Not Started |
| Step 5 | FCM 디바이스 등록 | W2 | ⬜ Not Started |
| Step 6 | Kafka → audit_logs 자동 기록 | W3 | ⬜ Not Started |
| Step 7 | FCM 푸시 + SES 이메일 알림 발송 | W3 | ⬜ Not Started |
| Step 8 | 관리자 테넌트/사용자 관리 | W3 | ⬜ Not Started |
| Step 9 | 인증/결제 전체 E2E 테스트 | W4 | ⬜ Not Started |
| Step 10 | P0 버그 수정 + 알림 안정화 | W4 | ⬜ Not Started |

### 사용 규칙

- 새 세션 시작 시 **Step 현황 테이블을 가장 먼저 확인**
- Step 시작 전 반드시 TASK_platform.md의 해당 Step **Instructions를 끝까지 읽기**
- Done When 미달 상태에서 Status → Done 처리 금지
- Step 완료 시 이 섹션의 테이블도 함께 업데이트

---

## 7. 모듈 구조 + 기술 스택

### Spring Modulith 패키지 구조

```
com.synapse.platform
├── auth/          OAuth 2.0, JWT, MFA(TOTP)
├── user/          사용자 프로필 관리
├── notification/  FCM 푸시, AWS SES 이메일
├── admin/         관리자 기능, Audit Log, Kafka Consumer
└── shared/        공통 유틸리티
```

### 기술 스택

| 항목 | 기술 |
|------|------|
| 언어 | Java 21 |
| 프레임워크 | Spring Boot 4.0.0 + Spring Modulith 1.3.0 |
| 빌드 | Gradle (Kotlin DSL) |
| DB | PostgreSQL 16 + Flyway 마이그레이션 |
| 캐시 | Redis 7 |
| 메시징 | Kafka + Avro + Schema Registry |
| 알림 | Firebase Admin SDK (FCM), AWS SES SDK |
| 결제 | Stripe Java SDK |
| 배포 | AWS EKS + Docker + ArgoCD |

---

## 8. 절대 금지 제약

### 아키텍처

- 모듈 간 순환 의존 금지 — `ApplicationModules.verify()` CI에서 자동 검증
- Refresh Token raw 원문 저장 금지 — DB에는 `token_hash`(SHA-256)만, Redis는 조회 캐시 (D-006)
- JWT 서명 알고리즘 RS256 고정 (HS256 사용 금지)
- Classic PAT 사용 금지 — fine-grained token만 허용

### Git

- `main` 브랜치 직접 push 절대 금지
- `git push --force` 금지
- `.env`, `*.key`, `*.pem` 파일 커밋 금지

### 코드

- 신규 코드 테스트 커버리지 80% 이상
- Stripe Webhook 서명 검증 필수 (replay attack 방지)
- Kafka Consumer at-least-once 보장 + DLQ 설정

---

## 9. Git 규칙 요약

> 상세 규칙: `docs/rules/13-git-rules.md`

### 브랜치

```
main
  └─ dev  (통합 개발 — 이 프로젝트 선택)
       └─ feature/PLAT-{NNN}-{설명}  ← 여기서 작업
            └─ PR → dev → approve 2명 → squash merge
```

**브랜치 prefix 규칙 (platform-svc)**

| prefix | 용도 | 예시 |
|--------|------|------|
| `feature/PLAT-NNN-` | 기능 개발 | `feature/PLAT-001-oauth-google` |
| `fix/PLAT-NNN-` | 버그 수정 | `fix/PLAT-003-jwt-expiry` |
| `hotfix/PLAT-NNN-` | 긴급 수정 | `hotfix/PLAT-012-jwt-leak` |
| `chore/PLAT-NNN-` | 설정/인프라 | `chore/PLAT-002-dockerfile` |
| `docs/PLAT-NNN-` | 문서 | `docs/PLAT-004-api-spec` |

### 커밋 메시지 (Conventional Commits)

```
<type>(<scope>): <subject>

[body — "왜" 이 변경이 필요한지]

[footer — Closes #N]
```

**platform-svc scope 값**: `auth`, `billing`, `notification`, `audit`, `infra`, `shared`

```
feat(auth): Google OAuth 로그인 구현
fix(billing): Stripe Webhook 중복 처리 방지
chore(infra): Dockerfile multi-stage 빌드 추가
test(notification): FCM 발송 실패 재시도 테스트
```

### PR 승인 정책

| 변경 종류 | 필요 승인 |
|----------|----------|
| 일반 feature/fix | `@team-lead` + 트랙 owner (2명) |
| Auth/보안 변경 | `@team-lead` + `@platform-owner` 이중 승인 |
| Hotfix | `@team-lead` 단독 |

### PR 본문 필수 섹션

```markdown
## 변경 사항
## 변경 유형 (feat/fix/chore 체크박스)
## 관련 이슈 (Closes #N)
## 테스트 방법
## 체크리스트 (셀프 리뷰 / 테스트 / Breaking change)
## 영향 받는 다른 서비스
## 이벤트/스키마 변경 여부
## 미러링/GitOps 영향
```

### 절대 금지

- `main` / `dev` 브랜치 직접 push
- `git push --force`
- `.env`, `*.key`, `*.pem` 파일 커밋
- Classic PAT 사용

---

## 10. 협업 인터페이스

| 대상 | 내용 | 방향 |
|------|------|------|
| 전체 서비스 | JWT 검증 (Gateway 연동) | 제공 → |
| @engagement-owner | gamification.* Kafka 이벤트 → notification 소비 | ← 수신 |
| @learning-card-owner | card.review.due Kafka 이벤트 → notification 소비 | ← 수신 |
| @team-lead | Gateway 인증 필터 협의 | 양방향 |
| Frontend (Flutter) | 로그인/회원가입 API | 제공 → |
