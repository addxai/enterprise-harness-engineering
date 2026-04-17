---
name: mock-engine
description: Mock Engine local development environment management. Use for starting/stopping mock services, loading test data, creating test scenarios, and troubleshooting startup issues. Triggers when the user mentions "start mock", "mock environment", "local dev environment", "mock-up", "test data", or "test scenarios".
---

# Mock Engine — Local Development Mock Environment Management

Provides unified mock infrastructure (MySQL, Redis, Kafka, MQTT, LocalStack, WireMock) via Docker Compose, supporting local development and integration testing.

## Description

Applicable scenarios:

- **Start/stop mock environment**: `make mock-up` one-command launch of all dependency services
- **Load test data**: Base fixtures auto-load; scenario fixtures load on demand
- **Create test scenarios**: Prepare preset data (SQL + Redis + WireMock stubs) for specific business flows
- **Troubleshoot startup issues**: Container status checks, port conflicts, data loading failures
- **Integration testing**: Manage mock infrastructure in automated tests via Java SDK or Go SDK

Prerequisites:

- Docker Compose v2.20+ (verify with `docker compose version`)
- A `mock/` directory exists at the project root (containing docker-compose.yml and Makefile)
- If there is no `mock/` directory, initialize from the mock-engine template:
  ```bash
  cp -r /path/to/mock-engine/core/templates/mock/ ./mock/
  # Modify project configuration in mock/Makefile (database name, password, etc.)
  ```

## Rules

### Operational Flow

**First-time initialization:**

```bash
cd mock/
make mock-init    # Download compose fragments
```

**Start Mock environment:**

```bash
make mock-up      # Start all services + wait for health checks + load data
make mock-status  # Verify all services are running normally
```

**Start the application (backend-service example):**

```bash
# The appName environment variable must be set
appName=your-app mvn spring-boot:run \
  -pl your-app \
  -Dspring-boot.run.profiles=dev-local,mock
```

**Load a test scenario:**

```bash
make mock-scenario SCENARIO=user-registration
# View available scenarios:
ls fixtures/scenarios/
```

**Stop/reset:**

```bash
make mock-down    # Stop services (preserve data)
make mock-clean   # Stop + delete data volumes
make mock-reset   # Full reset (clean + init + up)
```

### Default Port Mapping

| Service | Port | Environment Variable Override |
|------|------|-------------|
| MySQL | 13306 | MOCK_MYSQL_PORT |
| Redis (business) | 16379 | MOCK_REDIS_BUSINESS_PORT |
| Redis (readonly) | 16380 | MOCK_REDIS_READONLY_PORT |
| Redis (event) | 16381 | MOCK_REDIS_EVENT_PORT |
| Kafka | 19092 | MOCK_KAFKA_PORT |
| MQTT | 11883 | MOCK_MQTT_PORT |
| LocalStack | 14566 | MOCK_LOCALSTACK_PORT |
| WireMock | 19999 | MOCK_WIREMOCK_PORT |

### Test Data Management

**Base Fixtures (auto-loaded):** Place in `mock/fixtures/base/`, executed in filename order:

```
fixtures/base/
├── 01-seed-users.sql        # INSERT test users
├── 02-seed-devices.sql      # INSERT test devices
└── 03-seed-data.sql         # INSERT test data
```

**Scenario Fixtures (load on demand):** One subdirectory per scenario:

```
fixtures/scenarios/user-registration/
├── data.sql                 # MySQL data
├── redis-cmds.txt           # Redis CLI commands (one per line)
└── stubs-override/          # WireMock stub overrides
```

`redis-cmds.txt` format:
```
# Comment line
SET user:1001:token abc123
HSET device:DEV001 status online
EXPIRE user:1001:token 3600
```

**WireMock Stubs:** Place in `mock/stubs/<service-name>/`:

```json
{
  "request": {
    "method": "POST",
    "urlPath": "/stripe/v1/customers"
  },
  "response": {
    "status": 200,
    "jsonBody": { "id": "cus_mock_001" }
  }
}
```

Supports advanced features: conditional routing (queryParameters/bodyPatterns), dynamic templates (response-template), state machines (scenarioName), Webhook callbacks (serveEventListeners).

### Common Troubleshooting

**MySQL connection failed:**
```bash
docker ps --filter name=mock-mysql
docker logs mock-mysql
docker exec -e MYSQL_PWD=root123456 mock-mysql mysql -uroot -e "SELECT 1"
```

**Bind mount not taking effect (Docker-in-Docker):** SQL files not auto-loaded into MySQL:
```bash
docker exec -e MYSQL_PWD=root123456 -i mock-mysql mysql -uroot < mock/sql/init-schema.sql
```

**WireMock stubs not loaded:**
```bash
curl http://localhost:19999/__admin/mappings | python3 -m json.tool
docker cp mock/stubs/. mock-wiremock:/home/wiremock/mappings/
curl -X POST http://localhost:19999/__admin/mappings/reset
```

**Spring Bean missing (CloudBeanCondition):** Ensure the `appName=your-app` environment variable is set.

### SDK Integration (Automated Testing)

**Java (Testcontainers):**

```java
// pom.xml: <dependency>com.example:mock-engine</dependency>
MockInfraManager manager = MockInfraManager.fromProjectMockDir("./mock");
manager.startAll();
Map<String, String> props = manager.getAllProperties();
```

**Go:**

```go
// go.mod: require gitlab.example.com/tools/mock-engine/go
infra := mockinfra.New(mockinfra.WithProjectDir("./mock"))
infra.Start(ctx)
defer infra.Stop(ctx)
infra.LoadScenario(ctx, "user-registration")
```

## Examples

### Bad Example

```
User: Help me start the mock environment
AI: Let me just docker compose up directly

docker compose up -d

# Then directly start the application
mvn spring-boot:run -pl your-app
```

Problems:
- Did not enter the `mock/` directory
- Did not use `make mock-init` to initialize fragments
- Did not use `make mock-up` (skips health checks and data loading)
- Did not set `appName` environment variable or `mock` profile

### Good Example

```
User: Help me start the mock environment
AI: OK, let me check the mock directory and start the environment.

cd mock/
# Check if already initialized
ls .fragments/Makefile.include 2>/dev/null || make mock-init
# Start and wait for all services to be ready
make mock-up
# Verify service status
make mock-status

# Start the application (with correct environment variable and profile)
cd ..
appName=your-app mvn spring-boot:run \
  -pl your-app \
  -Dspring-boot.run.profiles=dev-local,mock

# Verify health check
curl -s http://localhost:7777/actuator/health
```

### Bad Example

```
User: I need to test the user registration flow
AI: Let me just call the registration API directly

curl -X POST http://localhost:7777/account/register \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@test.com"}'
```

Problems:
- Did not load the test scenario data first
- Did not provide an Authorization token
- Missing required request parameters

### Good Example

```
User: I need to test the user registration flow
AI: OK, let me load the registration test scenario data first, then test step by step.

# 1. Load user registration scenario data
cd mock/
make mock-scenario SCENARIO=user-registration

# 2. Login first to get an admin token
TOKEN=$(curl -s -X POST http://localhost:7777/account/login \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser1@mock.local","password":"password","loginType":99}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 3. Check if the email is available
curl -s -X POST http://localhost:7777/account/check-email \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"email":"newuser@mock.local"}'

# 4. Execute registration
curl -s -X POST http://localhost:7777/account/register \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  -d '{"email":"newuser@mock.local","password":"Test@1234","nickname":"TestUser"}'
```

## Related Resources

- mock-engine repository: `gitlab.example.com/tools/mock-engine`
- Design document: `mock-engine/docs/specs/2026-03-20-mock-engine-generalization-design.md`
