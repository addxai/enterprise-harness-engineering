# Universal Test Code Templates

> **When to read this file**: When writing test code, look up the template for the corresponding technology stack.

## Backend Go Unit Test

```go
func TestServiceName_MethodName(t *testing.T) {
    // Arrange
    mockRepo := mocks.NewMockRepository(t)
    svc := NewService(mockRepo)

    // Act
    result, err := svc.Method(context.Background(), input)

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, expected, result)
}
```

## Backend Go Integration Test

```go
func TestIntegration_ServiceFlow(t *testing.T) {
    if testing.Short() { t.Skip("skipping integration test") }

    // Setup: Docker Compose / Testcontainers
    container := setupTestDB(t)
    defer container.Terminate(context.Background())

    // Test full flow
}
```

## Backend Java/Spring Boot Integration Test

```java
@SpringBootTest
@ActiveProfiles({"test", "mock"})
class EvaluationIntegrationTest {
    @Autowired private MockMvc mockMvc;

    @Test
    void evaluate_noSubscription_returnsLockedTrue() throws Exception {
        // WireMock stub: Entitlement returns empty entitlements
        stubFor(get(urlPathMatching("/v1/features/.*"))
            .willReturn(okJson("{\"features\":[]}")));

        mockMvc.perform(get("/evaluate").param("userId", "10001"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].status").value("active"));
    }
}
```

## Flutter Widget Test

```dart
testWidgets('DeviceCard shows online status', (tester) async {
  await tester.pumpWidget(
    MaterialApp(home: DeviceCard(device: mockDevice)),
  );
  expect(find.text('Online'), findsOneWidget);
});
```

## Web (React) Component Test

```typescript
import { render, screen } from '@testing-library/react';

test('DashboardCard renders metric value', () => {
  render(<DashboardCard value={42} label="Sensors" />);
  expect(screen.getByText('42')).toBeInTheDocument();
});
```

## Embedded C++ GTest

```cpp
#include <gtest/gtest.h>
#include "<name>_cluster.h"

namespace iot::embedded::<name> {

class Mock<Name>HAL : public I<Name>HAL {
 public:
  void Set<Hardware>(type value) override { field_ = value; }
  type field_ = default_value;
};

TEST(<Name>ClusterTest, InitialState) { /* ... */ }
TEST(<Name>ClusterTest, BoundaryValue) { /* ... */ }

} // namespace
```

## Playwright E2E (General)

```typescript
import { test, expect } from "@playwright/test";

test.describe("L3 E2E Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(process.env.APP_URL!);
  });

  test("user login and dashboard load", async ({ page }) => {
    await page.fill('[data-testid="email"]', "test@example.com");
    await page.fill('[data-testid="password"]', "password");
    await page.click('[data-testid="login-btn"]');
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
  });
});
```

## Flutter Web + Playwright (Semantics Tree Black-Box E2E)

> Flutter Web exposes accessible DOM nodes via the Semantics Tree. Playwright locates elements through ARIA roles, **without modifying production code**.

```typescript
// helpers/flutter.ts
export async function waitForFlutterReady(page: Page) {
  await page.waitForSelector('flutter-view, flt-glass-pane', { timeout: 30_000 });
}
export async function enableSemantics(page: Page) {
  const placeholder = page.locator('flt-semantics-placeholder');
  if (await placeholder.isVisible()) await placeholder.click();
}

// Test case: Locate Flutter Widget via ARIA role
test('L3-FG-001 Device card shows locked badge @smoke', async ({ page }) => {
  await page.goto(`${BASE_URL}?scenario=new-user`);
  await waitForFlutterReady(page);
  await enableSemantics(page);
});
```

Playwright configuration notes: `timeout: 60_000` (Flutter Web cold start is slow), `workers: 1` (does not support parallelism), `webServer.command` uses `flutter run -d web-server --web-port 5173 --web-renderer html`.

## Wasm Digital Twin Test (Embedded-Specific)

```typescript
import { describe, it, expect, beforeAll } from "vitest";

describe("L2-2-LIGHT Digital Twin", () => {
  beforeAll(async () => {
    // Load scenario, wait for Wasm device ready
  });

  it("L2-2-LIGHT-001 App controls light on", async () => {
    // Command → Wasm → HAL Callback → Assert
    bridge.invokeDeviceCommand(deviceId, clusterId, commandId);
    await waitFor(() => halState.ledOn === true);
  });
});
```

---

## CI/CD General Pipeline Template

```yaml
# .gitlab-ci.yml general structure
stages:
  - build
  - test-l1 # L1 + L2-1 (every commit)
  - test-l2 # L2-2 integration (Nightly / Merge)
  - test-e2e # L3 E2E (pre-release)
  - quality # SonarQube / coverage

test-l1:
  stage: test-l1
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH
  script:
    - go test ./... -short -count=1 -coverprofile=coverage.out  # Backend
    - flutter test                                                # APP
    - npm run test:unit                                           # WEB
    - bazel test //clusters/...:all //devices/...:all             # Embedded

test-l2:
  stage: test-l2
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script:
    - docker compose -f docker-compose.test.yml up -d
    - go test ./... -count=1 -run Integration

test-e2e:
  stage: test-e2e
  rules:
    - if: $CI_COMMIT_TAG
  script:
    - npx playwright test
```

---

## Embedded-Specific Test Patterns

### State-Wait Pattern (Digital Twin Scenarios)

```typescript
async function waitForHubStatus(key: string, value: string, timeout = 10000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("Timeout")), timeout);
    const unsubscribe = bridge.onShadowDelta((delta) => {
      if (delta[key] === value) {
        clearTimeout(timer);
        unsubscribe();
        resolve(delta);
      }
    });
  });
}
```

### Forced Cycle Pattern (Embedded State Reset)

```typescript
beforeEach(async () => {
  // Force ON → OFF cycle to ensure device emits reset notification
  await invokeCommand(deviceId, ON);
  await waitForState("on");
  await invokeCommand(deviceId, OFF);
  await waitForState("off");
});
```
