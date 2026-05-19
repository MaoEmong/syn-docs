# Stripe Billing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stripe Checkout으로 유료 플랜 결제를 시작하고, Stripe Webhook으로 구독/결제 이력을 저장하며 tenant plan을 활성화/비활성화한다.

**Architecture:** `billing`은 Spring Modulith 신규 모듈로 추가한다. `billing -> user`는 기존 `UserApi`, `billing -> auth`는 신규 `TenantApi` named interface만 사용하며, auth/user 내부 repository나 entity를 직접 import하지 않는다. Stripe 호출은 `StripeClient` Bean을 통해 수행하고, Webhook 멱등성은 `processed_events.event_id` insert-first 방식으로 보장한다.

**Tech Stack:** Java 21, Spring Boot 4.0.0, Spring Modulith 2.0.6, Spring Data JPA, Flyway, Stripe Java 32.1.0, JUnit 5, Mockito, Spring Security Test, JaCoCo.

---

## File Map

**Modify**
- `build.gradle.kts`: Stripe SDK와 JaCoCo 설정 추가
- `src/main/resources/application.yml`: Stripe env 설정 추가
- `src/test/resources/application.yml`: 테스트용 Stripe 설정 추가
- `.env.example`: 로컬 compose용 Stripe placeholder 추가
- `src/main/java/io/synapse/platform/auth/domain/Tenant.java`: plan/status getter와 `activatePlan` 추가
- `src/main/java/io/synapse/platform/auth/config/SecurityConfig.java`: billing webhook permitAll 추가

**Create**
- `src/main/resources/db/migration/V24__create_subscriptions.sql`
- `src/main/resources/db/migration/V25__create_payment_history.sql`
- `src/main/resources/db/migration/V26__create_processed_events.sql`
- `src/main/java/io/synapse/platform/auth/api/package-info.java`
- `src/main/java/io/synapse/platform/auth/api/TenantInfo.java`
- `src/main/java/io/synapse/platform/auth/api/TenantApi.java`
- `src/main/java/io/synapse/platform/auth/TenantService.java`
- `src/main/java/io/synapse/platform/billing/package-info.java`
- `src/main/java/io/synapse/platform/billing/domain/PlanCode.java`
- `src/main/java/io/synapse/platform/billing/domain/SubscriptionStatus.java`
- `src/main/java/io/synapse/platform/billing/domain/Subscription.java`
- `src/main/java/io/synapse/platform/billing/domain/PaymentHistory.java`
- `src/main/java/io/synapse/platform/billing/domain/ProcessedEvent.java`
- `src/main/java/io/synapse/platform/billing/repository/SubscriptionRepository.java`
- `src/main/java/io/synapse/platform/billing/repository/PaymentHistoryRepository.java`
- `src/main/java/io/synapse/platform/billing/repository/ProcessedEventRepository.java`
- `src/main/java/io/synapse/platform/billing/config/StripeProperties.java`
- `src/main/java/io/synapse/platform/billing/config/StripeConfig.java`
- `src/main/java/io/synapse/platform/billing/dto/CheckoutSessionRequest.java`
- `src/main/java/io/synapse/platform/billing/dto/CheckoutSessionResponse.java`
- `src/main/java/io/synapse/platform/billing/dto/SubscriptionResponse.java`
- `src/main/java/io/synapse/platform/billing/exception/BillingException.java`
- `src/main/java/io/synapse/platform/billing/BillingService.java`
- `src/main/java/io/synapse/platform/billing/BillingController.java`
- `src/test/java/io/synapse/platform/billing/BillingServiceTest.java`
- `src/test/java/io/synapse/platform/billing/BillingControllerTest.java`
- `src/test/java/io/synapse/platform/billing/BillingRepositoryTest.java`

---

### Task 1: Build And Configuration

**Files:**
- Modify: `build.gradle.kts`
- Modify: `src/main/resources/application.yml`
- Modify: `src/test/resources/application.yml`
- Modify: `.env.example`

- [ ] **Step 1: Add Gradle plugin and dependency**

In `build.gradle.kts`, add `jacoco` to the `plugins` block:

```kotlin
plugins {
    java
    checkstyle
    jacoco
    id("org.springframework.boot") version "4.0.0"
    id("io.spring.dependency-management") version "1.1.7"
    id("com.github.spotbugs") version "6.0.9"
}
```

Add the Stripe dependency inside `dependencies`:

```kotlin
implementation("com.stripe:stripe-java:32.1.0")
```

- [ ] **Step 2: Add JaCoCo verification**

Append to `build.gradle.kts`:

```kotlin
jacoco {
    toolVersion = "0.8.12"
}

tasks.test {
    finalizedBy(tasks.jacocoTestReport)
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)
    reports {
        xml.required = true
        html.required = true
    }
}

tasks.jacocoTestCoverageVerification {
    dependsOn(tasks.test)
    violationRules {
        rule {
            element = "PACKAGE"
            includes = listOf("io.synapse.platform.billing*")
            limit {
                counter = "LINE"
                value = "COVEREDRATIO"
                minimum = "0.80".toBigDecimal()
            }
        }
    }
}

tasks.check {
    dependsOn(tasks.jacocoTestCoverageVerification)
}
```

- [ ] **Step 3: Add Stripe runtime configuration**

Append to `src/main/resources/application.yml`:

```yaml
stripe:
  api:
    key: ${STRIPE_API_KEY}
  webhook:
    secret: ${STRIPE_WEBHOOK_SECRET}
  plans:
    pro:
      price-id: ${STRIPE_PRO_PRICE_ID}
    team:
      price-id: ${STRIPE_TEAM_PRICE_ID}
    enterprise:
      price-id: ${STRIPE_ENTERPRISE_PRICE_ID}
```

- [ ] **Step 4: Add Stripe test configuration**

Append to `src/test/resources/application.yml`:

```yaml
stripe:
  api:
    key: sk_test_unit
  webhook:
    secret: whsec_test
  plans:
    pro:
      price-id: price_pro_test
    team:
      price-id: price_team_test
    enterprise:
      price-id: price_enterprise_test
```

- [ ] **Step 5: Add local compose placeholders**

Append to `.env.example`:

```dotenv
STRIPE_API_KEY=sk_test_local
STRIPE_WEBHOOK_SECRET=whsec_local
STRIPE_PRO_PRICE_ID=price_pro_local
STRIPE_TEAM_PRICE_ID=price_team_local
STRIPE_ENTERPRISE_PRICE_ID=price_enterprise_local
```

---

### Task 2: Flyway Migrations

**Files:**
- Create: `src/main/resources/db/migration/V24__create_subscriptions.sql`
- Create: `src/main/resources/db/migration/V25__create_payment_history.sql`
- Create: `src/main/resources/db/migration/V26__create_processed_events.sql`

- [ ] **Step 1: Create `V24__create_subscriptions.sql`**

```sql
CREATE TABLE subscriptions (
    id                     UUID         PRIMARY KEY,
    tenant_id              UUID         NOT NULL REFERENCES tenants(id),
    plan_code              VARCHAR(20)  NOT NULL,
    stripe_customer_id     VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    status                 VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE',
    current_period_start   TIMESTAMPTZ,
    current_period_end     TIMESTAMPTZ,
    canceled_at            TIMESTAMPTZ,
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX uq_subscriptions_tenant_active
    ON subscriptions(tenant_id) WHERE status = 'ACTIVE';
CREATE UNIQUE INDEX uq_subscriptions_stripe_sub_id
    ON subscriptions(stripe_subscription_id) WHERE stripe_subscription_id IS NOT NULL;
CREATE INDEX idx_subscriptions_tenant_id ON subscriptions(tenant_id);
```

- [ ] **Step 2: Create `V25__create_payment_history.sql`**

```sql
CREATE TABLE payment_history (
    id                       UUID         PRIMARY KEY,
    tenant_id                UUID         NOT NULL REFERENCES tenants(id),
    subscription_id          UUID         REFERENCES subscriptions(id),
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    amount                   INTEGER      NOT NULL,
    currency                 VARCHAR(3)   NOT NULL DEFAULT 'usd',
    status                   VARCHAR(20)  NOT NULL,
    paid_at                  TIMESTAMPTZ,
    created_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payment_history_tenant_id       ON payment_history(tenant_id);
CREATE INDEX idx_payment_history_subscription_id ON payment_history(subscription_id);
```

- [ ] **Step 3: Create `V26__create_processed_events.sql`**

```sql
CREATE TABLE processed_events (
    event_id     VARCHAR(255) PRIMARY KEY,
    event_type   VARCHAR(100) NOT NULL,
    received_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX idx_processed_events_received_at ON processed_events(received_at);
```

- [ ] **Step 4: Verify migration order**

Run:

```powershell
Get-ChildItem src/main/resources/db/migration | Select-Object Name
```

Expected: V24, V25, V26 files are present after the existing V1-V23 migrations.

---

### Task 3: Auth Tenant API Boundary

**Files:**
- Create: `src/main/java/io/synapse/platform/auth/api/package-info.java`
- Create: `src/main/java/io/synapse/platform/auth/api/TenantInfo.java`
- Create: `src/main/java/io/synapse/platform/auth/api/TenantApi.java`
- Create: `src/main/java/io/synapse/platform/auth/TenantService.java`
- Modify: `src/main/java/io/synapse/platform/auth/domain/Tenant.java`

- [ ] **Step 1: Create `auth/api/package-info.java`**

```java
@org.springframework.modulith.NamedInterface("tenant-api")
package io.synapse.platform.auth.api;
```

- [ ] **Step 2: Create `TenantInfo.java`**

```java
package io.synapse.platform.auth.api;

import java.util.UUID;

public record TenantInfo(UUID id, String plan, String status) {
}
```

- [ ] **Step 3: Create `TenantApi.java`**

```java
package io.synapse.platform.auth.api;

import java.util.Optional;
import java.util.UUID;

public interface TenantApi {
    Optional<TenantInfo> findById(UUID tenantId);

    void activatePlan(UUID tenantId, String planCode);
}
```

- [ ] **Step 4: Modify `Tenant.java`**

Add these methods to `Tenant`:

```java
public String getPlan() {
    return plan;
}

public String getStatus() {
    return status;
}

public void activatePlan(String planCode) {
    this.plan = planCode;
    this.updatedAt = OffsetDateTime.now();
}
```

- [ ] **Step 5: Create `TenantService.java`**

```java
package io.synapse.platform.auth;

import io.synapse.platform.auth.api.TenantApi;
import io.synapse.platform.auth.api.TenantInfo;
import io.synapse.platform.auth.repository.TenantRepository;
import java.util.Optional;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TenantService implements TenantApi {

    private final TenantRepository tenantRepository;

    public TenantService(TenantRepository tenantRepository) {
        this.tenantRepository = tenantRepository;
    }

    @Override
    public Optional<TenantInfo> findById(UUID tenantId) {
        return tenantRepository.findById(tenantId)
                .map(tenant -> new TenantInfo(tenant.getId(), tenant.getPlan(), tenant.getStatus()));
    }

    @Override
    @Transactional
    public void activatePlan(UUID tenantId, String planCode) {
        tenantRepository.findById(tenantId).ifPresent(tenant -> {
            tenant.activatePlan(planCode);
            tenantRepository.save(tenant);
        });
    }
}
```

---

### Task 4: Billing Domain And Repositories

**Files:**
- Create: `src/main/java/io/synapse/platform/billing/package-info.java`
- Create: `src/main/java/io/synapse/platform/billing/domain/*.java`
- Create: `src/main/java/io/synapse/platform/billing/repository/*.java`

- [ ] **Step 1: Create billing package declaration**

```java
@org.springframework.modulith.ApplicationModule
package io.synapse.platform.billing;
```

- [ ] **Step 2: Create enums**

`PlanCode.java`:

```java
package io.synapse.platform.billing.domain;

public enum PlanCode {
    FREE, PRO, TEAM, ENTERPRISE;

    public String value() {
        return name().toLowerCase();
    }
}
```

`SubscriptionStatus.java`:

```java
package io.synapse.platform.billing.domain;

public enum SubscriptionStatus {
    ACTIVE, CANCELED, PAST_DUE, TRIALING
}
```

- [ ] **Step 3: Create billing entities**

Create `Subscription`, `PaymentHistory`, and `ProcessedEvent` exactly as specified in `HANDOFF.md`. Keep `stripeCustomerId` nullable and use `UuidCreator.getTimeOrderedEpoch()` in `@PrePersist`.

- [ ] **Step 4: Create repositories**

`SubscriptionRepository.java`:

```java
package io.synapse.platform.billing.repository;

import io.synapse.platform.billing.domain.Subscription;
import io.synapse.platform.billing.domain.SubscriptionStatus;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SubscriptionRepository extends JpaRepository<Subscription, UUID> {
    Optional<Subscription> findByTenantIdAndStatus(UUID tenantId, SubscriptionStatus status);

    Optional<Subscription> findByStripeSubscriptionId(String stripeSubscriptionId);
}
```

`PaymentHistoryRepository.java`:

```java
package io.synapse.platform.billing.repository;

import io.synapse.platform.billing.domain.PaymentHistory;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PaymentHistoryRepository extends JpaRepository<PaymentHistory, UUID> {
}
```

`ProcessedEventRepository.java`:

```java
package io.synapse.platform.billing.repository;

import io.synapse.platform.billing.domain.ProcessedEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ProcessedEventRepository extends JpaRepository<ProcessedEvent, String> {

    @Modifying
    @Query(value = """
            INSERT INTO processed_events (event_id, event_type)
            VALUES (:eventId, :eventType)
            ON CONFLICT (event_id) DO NOTHING
            """, nativeQuery = true)
    int insertIfAbsent(@Param("eventId") String eventId, @Param("eventType") String eventType);
}
```

---

### Task 5: Stripe Configuration And DTOs

**Files:**
- Create: `src/main/java/io/synapse/platform/billing/config/StripeProperties.java`
- Create: `src/main/java/io/synapse/platform/billing/config/StripeConfig.java`
- Create: `src/main/java/io/synapse/platform/billing/dto/*.java`

- [ ] **Step 1: Create `StripeProperties.java`**

```java
package io.synapse.platform.billing.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "stripe")
public record StripeProperties(Webhook webhook, Plans plans) {
    public record Webhook(String secret) {
    }

    public record Plans(Plan pro, Plan team, Plan enterprise) {
    }

    public record Plan(String priceId) {
    }
}
```

- [ ] **Step 2: Create `StripeConfig.java`**

```java
package io.synapse.platform.billing.config;

import com.stripe.StripeClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(StripeProperties.class)
public class StripeConfig {

    @Bean
    public StripeClient stripeClient(@Value("${stripe.api.key}") String apiKey) {
        return StripeClient.builder()
                .setApiKey(apiKey)
                .build();
    }
}
```

- [ ] **Step 3: Create DTOs**

Create `CheckoutSessionRequest`, `CheckoutSessionResponse`, and `SubscriptionResponse` exactly as specified in `HANDOFF.md`.

---

### Task 6: Billing Service, Controller, And Security

**Files:**
- Create: `src/main/java/io/synapse/platform/billing/exception/BillingException.java`
- Create: `src/main/java/io/synapse/platform/billing/BillingService.java`
- Create: `src/main/java/io/synapse/platform/billing/BillingController.java`
- Modify: `src/main/java/io/synapse/platform/auth/config/SecurityConfig.java`

- [ ] **Step 1: Create `BillingException.java`**

```java
package io.synapse.platform.billing.exception;

import io.synapse.platform.shared.exception.BusinessException;

public class BillingException extends BusinessException {
    public BillingException(String errorCode, int status, String message) {
        super(errorCode, status, message);
    }
}
```

- [ ] **Step 2: Create `BillingService.java`**

Implement the service from `HANDOFF.md` with these fixed requirements:
- Add `import com.stripe.StripeClient;`.
- Checkout uses `stripeClient.checkout().sessions().create(...)`.
- Webhook uses `Webhook.constructEvent(...)`.
- Duplicate webhook events return after `processedEventRepository.insertIfAbsent(...) == 0`.
- `customer.subscription.deleted` cancels subscription and resets tenant plan to `PlanCode.FREE.value()`.

- [ ] **Step 3: Create `BillingController.java`**

Actual routes:
- `POST /api/v1/billing/checkout`
- `POST /api/v1/billing/webhooks`
- `GET /api/v1/billing/subscription`

Use `@RequestBody byte[]` for webhook payload.

For authenticated endpoints, do not parse `authentication.getPrincipal()` inline. Add a helper mirroring the existing MFA controller pattern, but throw `BillingException` from the billing module so the billing module does not import auth exceptions:

```java
private UUID currentUserId(Authentication authentication) {
    if (authentication == null) {
        throw new BillingException("PLAT-002", 401, "Authentication required");
    }
    try {
        return UUID.fromString(authentication.getName());
    } catch (IllegalArgumentException exception) {
        throw new BillingException("PLAT-002", 401, "Authentication required");
    }
}
```

Use `currentUserId(authentication)` in `/checkout` and `/subscription`.

- [ ] **Step 4: Permit webhook**

In `SecurityConfig`, add `"/api/v1/billing/webhooks"` to the existing `permitAll()` matcher list.

- [ ] **Step 5: Compile**

Run:

```powershell
.\gradlew.bat compileJava --no-daemon
```

Expected: compile succeeds. If Stripe SDK method names differ, adjust to the installed 32.1.0 API while preserving the same behavior.

---

### Task 7: Billing Tests

**Files:**
- Create: `src/test/java/io/synapse/platform/billing/BillingServiceTest.java`
- Create: `src/test/java/io/synapse/platform/billing/BillingControllerTest.java`
- Create: `src/test/java/io/synapse/platform/billing/BillingRepositoryTest.java`
- Create: `src/test/java/io/synapse/platform/billing/BillingSecurityIntegrationTest.java`

- [ ] **Step 1: Write repository tests with PostgreSQL**

Use `@DataJpaTest`, `@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)`, Testcontainers PostgreSQL, and Flyway enabled. Do not use the default H2 test database for these cases because the behavior under test depends on PostgreSQL DDL:
- partial unique index: `uq_subscriptions_tenant_active`
- native `ON CONFLICT (event_id) DO NOTHING`
- Flyway-created `processed_events`

Cover:
- subscription persist/find by tenant and active status
- active subscription uniqueness for one tenant
- processed event insert-first returns `1`, duplicate returns `0`

Create FK tenant rows in the repository test with native SQL before inserting subscriptions:

```sql
INSERT INTO tenants (
    id, name, slug, plan, status, tenant_type, region, settings, created_at, updated_at
) VALUES (
    ?, 'Billing Test Tenant', ?, 'free', 'active', 'personal', 'ap-northeast-2', '{}', NOW(), NOW()
)
```

- [ ] **Step 2: Write service tests**

Cover:
- checkout resolves default tenant from `UserApi`
- checkout maps PRO/TEAM/ENTERPRISE to Stripe price IDs
- checkout rejects FREE with `BILLING-005`
- invalid webhook signature throws `BILLING-002`
- duplicate webhook event does not run business mutation
- subscription deleted resets tenant plan to `free`

- [ ] **Step 3: Write controller tests**

Follow the existing controller-test pattern in `AuthControllerTest` and `MfaControllerTest`: use `MockMvcBuilders.standaloneSetup(...)`, `GlobalExceptionHandler`, and `LocalValidatorFactoryBean`.

Cover controller-local behavior:
- authenticated `POST /api/v1/billing/checkout` returns `200` and `checkoutUrl`
- missing principal for `POST /api/v1/billing/checkout` returns `401` problem response
- malformed principal returns `401` problem response
- `POST /api/v1/billing/webhooks` returns `200` when service succeeds
- `POST /api/v1/billing/webhooks` returns `400` when service throws `BILLING-002`
- authenticated `GET /api/v1/billing/subscription` returns `200`
- missing subscription maps to `404` when service throws `BILLING-003`

- [ ] **Step 4: Write security integration tests**

Use `@SpringBootTest` + `@AutoConfigureMockMvc` with a mocked `BillingService` if needed. Verify SecurityConfig behavior that standalone controller tests cannot prove:
- unauthenticated `POST /api/v1/billing/checkout` returns `401`
- unauthenticated `POST /api/v1/billing/webhooks` reaches the controller and returns `200`

- [ ] **Step 5: Run billing tests**

Run:

```powershell
.\gradlew.bat test --tests "io.synapse.platform.billing.*" --no-daemon
```

Expected: all billing tests pass.

---

### Task 8: Final Verification

**Files:**
- No planned edits.

- [ ] **Step 1: Check forbidden billing imports**

Run:

```powershell
rg -n "io\.synapse\.platform\.auth\.repository|io\.synapse\.platform\.auth\.domain|io\.synapse\.platform\.user\.repository|io\.synapse\.platform\.user\.domain" src/main/java/io/synapse/platform/billing
```

Expected: no output.

- [ ] **Step 2: Run Modulith structure test**

```powershell
.\gradlew.bat test --tests "io.synapse.platform.PlatformModuleStructureTest" --no-daemon
```

Expected: pass.

- [ ] **Step 3: Run full build**

```powershell
.\gradlew.bat build --no-daemon
```

Expected: pass, including JaCoCo coverage verification for `io.synapse.platform.billing*`.

- [ ] **Step 4: Final report**

Report:
- 작성/수정 파일 목록
- 실행한 검증 명령어와 결과
- Done When 충족 여부
- 실제 Stripe Test Mode 결제는 real Stripe key/webhook endpoint 없이는 수동 검증으로 남는지 여부

---

## Plan Review Notes

**What already exists**
- `PlatformApplication` already has `@ConfigurationPropertiesScan`; no app bootstrap change is needed.
- `GlobalExceptionHandler` already maps `BusinessException` to problem responses; `BillingException` should extend it rather than adding billing-specific exception advice.
- `MfaController` already has the safest `Authentication -> UUID` pattern; `BillingController` should mirror it using `BillingException`.
- `RefreshTokenServiceTest` already demonstrates Testcontainers PostgreSQL + Flyway wiring; billing repository tests should reuse that style for PostgreSQL-specific DDL.
- `JwtAuthenticationFilter` passes through requests without bearer tokens; `SecurityConfig.permitAll` is enough for webhook unauthenticated access, but a security integration test should prove it.

**NOT in scope**
- Refund handling: explicitly deferred by `TASK.md`.
- Plan upgrade/downgrade proration: explicitly deferred by `TASK.md`.
- Invoice PDF generation: explicitly deferred by `TASK.md`.
- Real Stripe Test Mode end-to-end payment in CI: requires real Stripe credentials and public webhook delivery.
- New billing UI: backend-only scope.

**Failure modes to cover**
- Stripe checkout API throws `StripeException`: service converts to `BILLING-001` 502.
- Missing user/default tenant: service converts to `BILLING-004` 404.
- Invalid webhook signature: service converts to `BILLING-002` 400 before any DB mutation.
- Duplicate Stripe event ID: `processed_events` insert returns `0`, business logic is skipped.
- Subscription cancel event arrives for unknown subscription: service no-ops and returns 200.
- Missing/malformed controller principal: controller returns `PLAT-002` 401 instead of 500.

**Data flow**

```text
POST /api/v1/billing/checkout
  -> BillingController.currentUserId
  -> BillingService.resolveTenantId(UserApi)
  -> StripeClient checkout session
  -> checkoutUrl

POST /api/v1/billing/webhooks
  -> raw byte[] payload
  -> Webhook.constructEvent
  -> processed_events insert-first
  -> checkout.session.completed -> subscriptions + tenant.plan
  -> invoice.paid -> payment_history
  -> customer.subscription.deleted -> subscriptions cancel + tenant.plan free
```

**Parallelization**

| Lane | Work | Depends on |
|------|------|------------|
| A | Gradle/config + migrations | none |
| B | Auth `TenantApi` boundary | none |
| C | Billing domain/repositories | A migrations for repository tests |
| D | Stripe config/DTO/service/controller | B and C |
| E | Tests/final verification | D |

Recommended execution: A and B can be implemented first in parallel if using separate worktrees, then C, then D, then E. In this single workspace, execute sequentially to avoid merge conflicts in `build.gradle.kts` and shared test config.

---

## Self-Review

**Spec coverage:** Stripe dependency/config, V24/V25/V26 migrations, TenantApi boundary, billing module/domain/repository, StripeClient, checkout API, webhook API, subscription query API, security permitAll, idempotency, cancellation reset, tests, Modulith verification, JaCoCo verification을 포함한다.

**Implementation rule:** 실제 API 경로는 `/api/v1/billing/...`를 사용한다. `TASK.md`의 `/billing/...` 표기는 원본 작업 문서의 축약 표기로 취급한다.

**Residual risk:** Stripe Java 32.1.0의 일부 메서드 시그니처는 `compileJava`로 확정한다. SDK API가 문서 예시와 다르면 동일 동작을 유지하는 32.1.0 방식으로 조정한다.
