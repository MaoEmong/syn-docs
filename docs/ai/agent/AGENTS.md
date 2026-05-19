# AGENTS.md — synapse-platform-svc

> Codex가 세션 시작 시 자동으로 로드하는 파일입니다.
> 코드 작성 전 반드시 아래 순서대로 컨텍스트를 파악하세요.

---

## 역할

Worker. 코드 작성, 테스트 작성, 리팩토링을 담당합니다.
설계 결정은 하지 않습니다. HANDOFF.md의 명세대로 구현합니다.
상세 행동 지침 → `docs/ai/agent/worker.md`

---

## 세션 시작 시 필수 확인 (순서 준수)

```
1. docs/ai/current/HANDOFF.md   — 요청 내용 + 출력 형식 확인
2. docs/ai/current/CONTEXT.md   — 확정된 것 + 활성 제약 확인
3. docs/ai/current/TASK.md      — Done When 기준 확인
```

---

## 프로젝트 기본 정보

- **언어**: Java 21
- **프레임워크**: Spring Boot 4.0.0 + Spring Modulith 1.3.0
- **빌드**: `./gradlew build` (Gradle Kotlin DSL)
- **패키지 루트**: `com.synapse.platform`
- **테스트 실행**: `./gradlew test`
- **Modulith 검증**: `./gradlew test --tests '*ModuleStructureTest'`

---

## 모듈 구조

```
com.synapse.platform
├── auth/          OAuth 2.0 (Google/GitHub), JWT, MFA(TOTP)
├── user/          사용자 프로필 관리
├── notification/  FCM 푸시, AWS SES 이메일
├── admin/         관리자 기능, Audit Log, Kafka Consumer
└── shared/        공통 유틸리티 (모듈 간 공유 허용)
```

모듈 간 직접 import 금지 (shared 제외). 위반 시 `ApplicationModules.verify()` 실패.

---

## 절대 금지

| 금지 항목 | 이유 |
|----------|------|
| Refresh Token raw 원문 저장 | DB에는 token_hash(SHA-256)만, Redis는 캐시 (D-006) |
| JWT 서명 HS256 사용 | RS256 고정 |
| 모듈 간 직접 import | Modulith 경계 위반 |
| System.out.println | Logger 사용 |
| 코드 설명 주석 | 잘 지어진 이름으로 대체 |
| 테스트 없는 신규 코드 | 커버리지 80% 이상 필수 |

---

## 코드 작성 규칙

### 레이어별 테스트 방식

| 레이어 | 테스트 방식 |
|--------|------------|
| Service | `@ExtendWith(MockitoExtension.class)` 단위 테스트 |
| Controller | `@WebMvcTest` 슬라이스 테스트 (401/403 케이스 포함) |
| Repository | `@DataJpaTest` |
| 통합 | `@SpringBootTest` |
| Kafka | Embedded Kafka |

### 룰 파일 매핑

작업 시작 전 해당 룰 파일을 확인하세요.

| 작업 유형 | 참고 룰 |
|----------|--------|
| JWT / OAuth | `docs/rules/06-auth-token.md` |
| Spring 전반 | `docs/rules/07-platform-spring.md` |
| Kafka | `docs/rules/08-kafka-event.md` |
| 보안 | `docs/rules/01-security.md` |
| 코드 품질 | `docs/rules/04-quality.md` |

---

## 빌드 / 검증 명령어

```bash
# 전체 빌드
./gradlew clean build

# 테스트만
./gradlew test

# Modulith 구조 검증
./gradlew test --tests '*ModuleStructureTest'

# 특정 모듈 테스트
./gradlew test --tests 'com.synapse.platform.auth.*'
```

---

## 출력 형식

HANDOFF.md에 명시된 형식을 따릅니다.
명시되지 않은 경우: **파일 경로 + 전체 코드 블록**으로 제출합니다.

구현 완료 후 반드시 포함할 항목:
- 작성한 파일 목록
- 실행한 테스트 명령어 + 결과
- Done When 항목 충족 여부 체크
