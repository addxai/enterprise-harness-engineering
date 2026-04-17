---
name: multi-worktree-dev
description: Design and implementation guide for parallel multi-worktree development environments. Use whenever the user mentions multi-worktree development, git worktree, port conflicts, concurrent dev environments, feature branch isolation, local environment setup, or multi-developer collaboration conflicts. Even if the user casually says "we have several worktrees running simultaneously", this Skill should be triggered to guide them toward a proper layered environment.
---

# multi-worktree-dev

Handbook for designing and deploying parallel multi-worktree development environments — helps teams define a layered environment strategy that supports concurrent worktree development, parallel testing, and stable shared infrastructure.

## Core Design Goals

| Goal | Specific Design |
|------|----------|
| Zero complexity | Creating a new worktree requires no manual configuration — `make dev` handles all setup automatically |
| Parallel safety | Tests across multiple worktrees run fully in parallel without blocking each other |
| Shared channel exclusivity | Singleton channels like Feishu WS are held by only one worktree at a time |
| Instant layer switching | Layer 1 stays running; switching worktrees only requires starting L2/L3 |
| Zero port conflicts | Ports are assigned via **automatic hash offset**; developers never need to manually edit configuration |
| Smooth development | Layer 3 is fully hot-reloaded; code changes require no process restart |

## Description

This Skill covers designing a local environment system from scratch that supports parallel multi-branch development. The core idea is the following **three-layer separation** structure:

| Layer                          | Description                                                           | Lifecycle               |
| ----------------------------- | -------------------------------------------------------------- | ---------------------- |
| Layer 1 — Global Shared Infra      | Database, cache, message queue (Kafka/RabbitMQ), LLM proxy, and other heavyweight services | Always running, shared across all branches     |
| Layer 2 — Worktree-Exclusive Infra | Services that require isolation (e.g., Temporal, secret store)                    | Started/stopped with the worktree  |
| Layer 3 — Host Processes           | Application services (API, Worker, frontend)                              | Hot-reloaded, run directly on the host machine |


## Rules

### Rule 0 — Scan the codebase first; auto-discover services

When receiving a layered design request, **do not start by asking the user "what services do you have"**. First proactively scan the codebase, auto-discover dependencies, then provide an evidence-based layering recommendation.

**Scanning order (by priority)**:

1. **docker-compose files** (most direct)

   ```bash
   find . -name "docker-compose*.yml" -o -name "docker-compose*.yaml" | head -20
   ```

   Parse the `services:` blocks to extract all service names and images.

2. **requirements / dependency manifests** (infer middleware)

   ```bash
   # Python
   grep -rE "(redis|postgres|psycopg|sqlalchemy|temporalio|kafka|rabbitmq|celery|vault|consul)" \
     requirements*.txt pyproject.toml 2>/dev/null

   # Node.js
   grep -rE "(redis|pg|sequelize|temporal|kafka|amqp|consul)" \
     package.json 2>/dev/null

   # Go
   grep -rE "(go-redis|lib/pq|temporal|kafka|vault)" go.mod 2>/dev/null
   ```

3. **Environment variable files** (discover existing configurations)

   ```bash
   cat .env.example .env.local.example 2>/dev/null | grep -E "_URL=|_HOST=|_PORT="
   ```

4. **Makefile / startup scripts** (discover existing dev workflows)

   ```bash
   grep -E "^(dev|start|up|test)" Makefile 2>/dev/null | head -20
   cat scripts/dev.sh scripts/start.sh 2>/dev/null | head -50
   ```

5. **Dockerfile files** (discover application service build targets)
   ```bash
   find . -name "Dockerfile*" | head -20
   ```
   Parse each Dockerfile's directory and `EXPOSE` ports to infer which L3 service it is (vs. L1/L2 middleware from step 1's docker-compose).

After scanning, compile the discovered service list and, combined with Rule 1's decision tree, present a **pre-filled layering recommendation table** for the user to confirm or correct, rather than having the user describe from scratch.

> **Why scan first?** Users often cannot list all dependencies completely, and the service names they mention may differ from those in the codebase. Discovering directly from the codebase is more accurate and saves back-and-forth communication time.

### Rule 1 — Service Layering Decision

Based on Rule 0's scan results, classify each service using the following decision tree:

```
Can the service be shared across branches (data overwrites do not affect other branches)?
  └─ Yes, and startup cost is high (> 30s) → Layer 1 (global shared)
       └─ No, and branch data isolation is needed → Layer 2 (worktree-exclusive, dynamic port)
            └─ No, it is the application code itself → Layer 3 (host process, hot-reload)
```

**Common classification examples**:

| Service                  | Layer | Reasoning                                       |
| --------------------- | ---- | ------------------------------------------ |
| PostgreSQL / MySQL    | L1   | Shared schema across branches; isolate by different DB names |
| Redis                 | L1   | Key prefix isolation is sufficient                           |
| LiteLLM / model proxy    | L1   | Stateless, safe to share                           |
| Kafka / RabbitMQ      | L1   | Shared message queue; isolate by topic/queue        |
| Temporal              | L2   | Requires namespace isolation                        |
| Vault / Consul        | L2   | Requires independent secret paths                       |
| API Gateway / Backend | L3   | Hot-reloaded code, runs independently per branch                   |
| Frontend Dev Server       | L3   | Vite HMR / Next.js dev                     |

### Rule 2 — Port Management (Multi-Worktree Concurrency)

When running multiple worktrees concurrently, L2 and L3 services need **dynamic port offsets** to avoid port conflicts.

**Dual-file overlay strategy**:

| File            | Contents                    | Maintained By                                 |
| --------------- | ----------------------- | -------------------------------------- |
| `.env.local`    | Default ports, API Keys      | Developer writes once; commit `.example` to Git |
| `.worktree.env` | Offset ports, overrides above | Auto-generated by `make dev`; add to `.gitignore` |

With a single worktree, `.worktree.env` is not generated and `.env.local` defaults take effect directly; with concurrent worktrees, the offset kicks in automatically.

**Port hash algorithm example (bash)**:

```bash
# Deterministic hash offset based on worktree path (range 0-49)
WT_HASH=$(echo -n "$(pwd)" | md5sum | cut -c1-4)
PORT_OFFSET=$(( 16#${WT_HASH} % 50 ))

# Write to .worktree.env
echo "GATEWAY_PORT=$(( 8000 + PORT_OFFSET ))" > .worktree.env
echo "DASHBOARD_PORT=$(( 3000 + PORT_OFFSET ))" >> .worktree.env
echo "TEMPORAL_PORT=$(( 7233 + PORT_OFFSET ))" >> .worktree.env
```

**Overlay loading at startup**:

```bash
# L2 (docker compose)
docker compose --env-file .env.local --env-file .worktree.env up -d

# L3 (host process)
source .env.local && source .worktree.env
uvicorn app.main:app --port ${GATEWAY_PORT:-8000} --reload
```

### Rule 3 — Exclusive Switching for Shared Channels

Feishu WS, WebSocket push endpoints, and other **global singleton channels** can only be held by one worktree at a time.

**Switching mechanism design requirements**:

1. When `make dev` is triggered, automatically execute `scripts/feishu-switch.sh $(PWD)`
2. The script iterates over all worktrees and sends a "close channel" command to other worktrees (update `.worktree.env` + restart the corresponding L3 process)
3. Only enable the channel in the current worktree
4. `make test*` **does not trigger** this script — tests do not seize the shared channel

**feishu-switch.sh logic skeleton**:

```bash
#!/usr/bin/env bash
CURRENT_WT="$1"

# Iterate over all worktrees
git worktree list --porcelain | grep "^worktree " | awk '{print $2}' | while read wt; do
  if [ "$wt" != "$CURRENT_WT" ]; then
    # Close Feishu WS in other worktrees
    echo "FEISHU_WS_ENABLED=false" >> "$wt/.worktree.env"
    # Trigger hot-reload of the corresponding gateway (uvicorn --reload detects file changes)
    touch "$wt/services/gateway/main.py"
  fi
done

# Enable in current worktree
echo "FEISHU_WS_ENABLED=true" >> "$CURRENT_WT/.worktree.env"
```

### Rule 4 — Idempotent ensure-up Pattern

All startup scripts must be **idempotent**: calling multiple times produces the same result without creating duplicate resources.

```bash
# Recommended pattern: check first, then start
ensure_service_up() {
  local service=$1
  if ! docker ps --filter "name=${service}" --filter "status=running" -q | grep -q .; then
    docker compose up -d "${service}"
  fi
}
```

`make test*` internally calls `ensure_service_up` — no need to manually run `make dev` first.

### Rule 4b — Cross-Platform Background Process Startup

Layer 3 host processes need to detach from the parent shell (not killed by SIGHUP when `make` exits); different systems require different commands:

| Platform | Recommended Approach | Notes |
|------|---------|------|
| **macOS** | `nohup cmd & disown $!` | `setsid` is not available on macOS |
| **Linux** | `nohup cmd & disown $!` | Also works; `setsid nohup cmd &` is possible but unnecessary |
| **Windows (Git Bash/WSL)** | `nohup cmd & disown $!` | Git Bash has built-in `nohup`; `disown` is a bash builtin |
| **Windows (native cmd/PowerShell)** | `Start-Process -NoNewWindow` / `start /B` | Only for non-bash scenarios |

**Cross-platform unified approach** (in `bash`/`zsh` scripts):

```bash
_start_bg() {
  local logfile="$LOG_DIR/${1}.log"
  mkdir -p "$LOG_DIR"
  nohup "${@:2}" > "$logfile" 2>&1 &   # nohup: ignore HUP signal
  local pid=$!
  disown "$pid"                          # disown: remove from shell job table; make exit does not propagate HUP
  echo "$pid"
}

# Usage
pid=$(_start_bg "gateway" bash -c "cd services/gateway && uvicorn src.main:app --reload")

```

> **Common pitfall**: `setsid` is Linux-only (util-linux package); on macOS it reports `command not found`.
> `nohup + disown` is the POSIX-compatible solution, unified across all three platforms.

> **disown scope limitation**: `nohup cmd & disown $!` must be executed within the **same shell context** (same function body or same `{}` block); it cannot span `&&` chains. Inside a subshell within a `&&` chain, `disown` cannot find the job. Wrapping in a function (like `_start_bg` above) ensures correct scope.


### Rule 4c — Post-Startup Health Verification (No Faking Ready)

After Layer 3 processes start, `make dev` **must perform real port/HTTP health probing** rather than simply printing "=== Dev environment ready ===".

**Correct verification logic**:

```bash
_check_health() {
  local name="$1" url="$2" port="$3"
  if [ -n "$url" ]; then
    curl -sf --max-time 3 "$url" >/dev/null 2>&1 \
      && echo "  ✓ ${name}" \
      || echo "  ✗ ${name} (not ready — check .logs/${name}.log)"
  else
    nc -z localhost "$port" 2>/dev/null \
      && echo "  ✓ ${name}:${port}" \
      || echo "  ✗ ${name}:${port} (not ready — check .logs/${name}.log)"
  fi
}

sleep 2  # brief grace for port binding
_check_health "gateway"   "http://localhost:${GATEWAY_PORT}/health" ""
_check_health "sandbox"   "http://localhost:${SANDBOX_PORT}/health" ""
_check_health "temporal"  "" "${TEMPORAL_HOST_PORT}"
```

**Mandatory requirements**:
- Every Layer 3 service must have a port or HTTP health probe
- On failure, output `✗ service (not ready — check .logs/service.log)` with log path guidance
- A Layer 3 process PID does not mean the service is ready (uvicorn needs 1-2s to bind the port)
- Checking only PID existence and declaring ready is prohibited
- "Dev environment ready" must not appear while any service is actually down

**Optional services like Vault**: If the service is not configured (Docker cannot pull the image, etc.), display `(not running)` instead of `✗`, and do not block the startup flow.

### Rule 5 — Test Parallel Safety

Test command design standards (naming follows the L1/L2/L3 layer convention from the `testing-strategy` Skill):

| Layer | Command | Infra Dependency | Affects Shared Channel |
|------|------|-----------|----------------|
| L1 Unit | `make test-unit` | None (pure code) | No |
| L2 Integration | `make test-l2` | L1 + L2 (auto ensure) | No |
| L3 E2E | `make test-l3` | L1 + L2 + L3 services | No |
| L4 UAT | `make test-l4-uat` | All (requires real Staging environment) | No |
| Smoke | `make smoke` | All (requires make dev to run first) | No |
| Full Regression | `make regression` | All (CI quality gate) | No |

> **Core constraint: `make test*` commands do not open, close, or touch singleton channels like Feishu WS.**
>
> Specifically:
> - Does not call `feishu-switch.sh` (does not seize or switch)
> - Does not set `FEISHU_WS_ENABLED=true` (does not proactively enable)
> - Does not set `FEISHU_WS_ENABLED=false` and restart gateway (does not proactively disable)
> - Preserves the current worktree's WS state as-is; state is unchanged after tests complete
>
> **Purpose**: While worktree-A is running `make dev` and holding the WS, worktree-B can safely run `make test-l2` without interrupting A's connection.

For detailed layered testing strategy (coverage gates, mock isolation, TDD debugging, CI pipeline configuration), refer to the `testing-strategy` Skill.


### Rule 6 — Hot-Reload and Watch Auto-Build

Layer 3 services should all be configured with hot-reload — code changes **require no manual process restart**.

**Select watch tool by service type**:

| Service Type | Recommended Tool | Startup Command | Trigger Condition |
|---------|---------|---------|--------|
| Python API (FastAPI/Flask) | `uvicorn --reload` | `uvicorn app.main:app --reload --reload-dir src` | `.py` file changes |
| Python Worker (Temporal/Celery) | `watchfiles` | `watchfiles 'python worker.py' src/` | `.py` file changes |
| Node.js / TypeScript Worker | `tsx watch` / `nodemon` | `tsx watch src/worker.ts` | `.ts/.js` changes |
| Frontend (React/Next.js/Vite) | Built-in HMR | `vite dev` / `next dev` | Instant partial browser refresh, no manual refresh |
| Go service | `air` | `air -c .air.toml` | `.go` file changes trigger auto-recompile |
| Static files / config | `watchexec` | `watchexec -e yaml,toml -- ./restart.sh` | Config file changes trigger restart script |
| Flutter Web | `flutter build web` + Vite hosting | Build first, Vite hosts `/build/web/`; dev with `flutter run -d chrome` | Dart file changes trigger Hot Restart |

**Multi-worktree note**: Each worktree's watch processes are independent; ports are already isolated via Rule 2's offset, so no extra handling is needed.

#### Container Hot-Reload (Volume Mount Mode)

For L3 services running as **containers** (not host processes), hot-reload is achieved by **mounting the source directory** rather than rebuilding the image:

```yaml
# docker-compose.dev.yml — Dev mode: mount host source code
services:
  sandbox:
    image: your-org/your-image:latest   # Image only provides the runtime environment
    volumes:
      - ./services/sandbox:/app/src  # Host source → inside container
    command: tsx watch /app/src/index.ts  # Container watcher monitors changes
    environment:
      - NODE_ENV=development
```

```yaml
# docker-compose.prod.yml — Production mode: code baked into image
services:
  sandbox:
    image: your-org/your-image:${IMAGE_TAG}  # Code packaged at image build time
    # No volumes, no watcher, code is immutable
```

**Key differences between dev and production**:

| Dimension | Dev Mode (volume mount) | Production Mode (baked image) |
|------|------------------------|----------------------|
| Code source | Real-time mount from host directory | Frozen into image at build time |
| Hot-reload | Container watcher monitors changes | Requires image rebuild for code changes |
| Image build | Not needed (fast startup) | CI build → push to Harbor |
| Isolation | Low (shares source with host) | High (completely independent) |
| Use case | Local development iteration | staging / prod deployment |

**In a multi-worktree environment**, dev mode volume mount paths already contain the worktree's absolute path, so different worktrees are naturally isolated — no extra handling is needed.

**Scan for existing watch configuration** (check alongside Rule 0 scan):

```bash
# Check if existing docker-compose distinguishes dev/prod modes
ls docker-compose*.yml
grep -l "volumes:" docker-compose*.yml   # Files with volumes are dev-style
grep -l "NODE_ENV=production" docker-compose*.yml  # Production mode

# Check if services already have watch configured
grep -rE "(--reload|watchfiles|nodemon|tsx watch|air|HMR)" \
  Makefile scripts/*.sh 2>/dev/null
```

If the project has only a single `docker-compose.yml` without dev/prod distinction, recommend splitting into `docker-compose.yml` (base) + `docker-compose.dev.yml` (dev override).

### Rule 7 — Dev Lifecycle Command Design

`make dev` is not the only command — a complete lifecycle command set is needed:

| Command | Behavior | Typical Implementation |
|------|------|--------|
| `make dev` | Start current worktree (L2 + L3), switch shared channels | ensure L1 → ensure L2 → start L3 with watch → feishu-switch |
| `make dev-down` | Stop current worktree (L2 + L3 stop, **L1 keeps running**) | stop L3 pids → docker compose stop L2 services |
| `make dev-check` | Check health status of all services | curl each service health endpoint, list UP/DOWN |
| `make dev-restart` | Quick restart L3 processes (without restarting L2) | kill L3 pids → restart with watch |

**Two modes for E2E testing** (applicable to L3 services with external API dependencies):

| Mode | External Dependency Handling | Applicable Stage |
|------|------------|---------|
| **Mock mode** (daily) | Use mock server to simulate external APIs | Daily development iteration; fast startup, no extra dependencies |
| **Real mode** (pre-acceptance) | Connect to real external services/environments | Pre-release acceptance; verify real integration behavior |



**Prerequisite checks** (auto-verified before `make dev` starts):

```bash
check_prerequisites() {
  command -v docker >/dev/null || { echo "❌ docker not found"; exit 1; }
  command -v uv >/dev/null    || { echo "❌ uv not found"; exit 1; }
  command -v node >/dev/null  || { echo "❌ node not found"; exit 1; }
  docker info >/dev/null 2>&1 || { echo "❌ Docker daemon not running"; exit 1; }
  echo "✅ prerequisites OK"
}
```

### Rule 8 — Documentation Structure (Quad-File Pattern)

For each service with independent deployment complexity, documentation is organized into four files:

```
docs/deployment/
  overview.md    # Architecture overview, Mermaid flow diagrams (local → CI → CD)
  local-dev.md   # Split into "User Guide" and "Implementation Details" sections
  ci.md          # CI pipeline design, testing strategy
  cd.md          # K8s / Terraform / ArgoCD configuration
```

`local-dev.md` must have two sections:

- **User Guide**: Commands and results only, for developers
- **Implementation Details**: Explains the design rationale, for maintainers

### Rule 9 — Operational Red Lines

- **Prohibited**: Modifying Layer 1 docker-compose configuration without notifying other running worktrees
- **Prohibited**: Calling shared channel switching scripts in `make test*`
- **Prohibited**: Committing `.worktree.env` to Git (must be gitignored)
- **Prohibited**: Hard-coding port numbers in a multi-worktree environment (must use environment variables + offset)
- When Layer 1 services go down, **investigate shared resources first** before restarting to avoid affecting other worktrees running tests
- **Bare commands that change state must be synced back to make/scripts**: Running `docker compose up/down`, `uvicorn`, `pytest`, etc. directly changes system state (starts processes, occupies ports, writes pid files), but make and scripts are unaware — next time `make dev` runs, ports are already occupied, pid files are stale, and infra state is mismatched, causing make to fail.
  - If bare commands were used for temporary debugging, after debugging either **kill the manually started processes** or **codify the changes into scripts/**, keeping make and actual state consistent.
  - Correct: bare command debugging → kill processes after debugging → `make dev` takes over
  - Wrong: Start sandbox with a bare command, don't kill it, run `make dev` directly → port already in use
- **Bare commands are prohibited**: All development/test operations must use existing `make` targets. First check if existing targets cover the need; if not, check if parameter combinations can achieve it.
- **Make targets are fixed; adding new ones arbitrarily is prohibited**: The allowed targets are a fixed set:
  - Development lifecycle: `make dev`, `make dev-check`, `make dev-down`
  - Testing: `make test-unit`, `make test-l2`, `make test-l3`, `make test-l4-uat`, `make smoke`, `make regression`, `make test-cov`, `make test-watch`
  - Build/quality: `make lint`, `make format`, `make build-*`
  - New targets that do not belong to any of the above categories must not be added.

### Rule 10 — Flutter Web E2E Testing (Playwright + Semantics Tree)

Flutter Web E2E testing uses Playwright to operate the Flutter Semantics tree (accessible DOM tree) without modifying Flutter production code.

**Core approach** (based on iot-system-template):

| Step | Description |
|------|------|
| Wait for ready | Poll for `<flutter-view>` or `<flt-glass-pane>` to appear |
| Enable Semantics | Click Flutter's built-in "Enable accessibility" button |
| Element location | Locate via ARIA role attributes (`role="button"`, `role="switch"`, etc.) |
| Interaction | Standard Playwright click/fill/assert operations |

**Playwright configuration notes**:

```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './tests/l3-browser',
  timeout: 60_000,           // Flutter Web loads slowly
  expect: { timeout: 15_000 },
  workers: 1,                // Flutter Web does not support parallelism
  projects: [{
    name: 'chromium',
    use: {
      headless: true,
      screenshot: 'only-on-failure',
      video: 'retain-on-failure',
    },
  }],
  webServer: {
    command: 'npm run dev',  // or vite dev
    port: 5173,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
```

**Test helper functions**:

```typescript
async function waitForFlutterReady(page: Page) {
  await page.waitForSelector('flutter-view, flt-glass-pane', { timeout: 30_000 });
}

async function enableFlutterSemantics(page: Page) {
  const btn = page.locator('flt-semantics-placeholder');
  if (await btn.isVisible()) await btn.click();
}
```

**Multi-worktree note**: The Playwright webServer port is automatically isolated via `.worktree.env` offset, so multiple worktrees can run E2E tests in parallel without conflicts.

## Examples

### Bad

```
New project layering design:
- Temporal in Layer 1 (all worktrees share the same Temporal namespace)
  → Problem: worktree-A's Workflows will be picked up by worktree-B's Workers

- make test calls feishu-switch.sh
  → Problem: running a test seizes a colleague's Feishu connection

- GATEWAY_PORT=8001 hard-coded in code
  → Problem: the second worktree gets a port conflict on startup
```

### Good

```
New project layering design:
- Temporal → Layer 2 (each worktree has independent port + namespace: wt-{hash})
- make test* → only ensures L1/L2; does not call feishu-switch.sh
- Ports computed automatically via PORT_OFFSET=$(hash(pwd) % 50), written to .worktree.env

Standard multi-worktree concurrent development flow:
  worktree-A: make dev       → holds Feishu WS, receives messages normally
  worktree-B: make test-l2   → runs integration tests in parallel without affecting A's connection
  Switch development: worktree-A make dev-down → worktree-B make dev (instant)
```

## References

- [testing-strategy Skill](../testing-strategy/SKILL.md) — Complete L1/L2/L3/L4 layered testing strategy with CI quality gates and TDD debugging workflow
- [YourProject local dev environment docs](../../YourProject/.claude/worktrees/local-dev/docs/deployment/local-dev.md) — Reference implementation for L1/L2/L3 layering
- [YourProject deployment architecture overview](../../YourProject/.claude/worktrees/local-dev/docs/deployment/overview.md) — Mermaid architecture diagrams + full CI/CD chain
