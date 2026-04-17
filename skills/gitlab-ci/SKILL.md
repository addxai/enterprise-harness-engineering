---
name: gitlab-ci
description: Create and review .gitlab-ci.yml files based on GitLab CI best practices and company standards. Use when creating CI/CD pipelines for new projects, reviewing existing .gitlab-ci.yml, or optimizing pipeline configuration.
---

# GitLab CI

## Description

Create and review `.gitlab-ci.yml` files. Based on GitLab CI official best practices, DRY/SSOT design patterns, and company standards.

**Applicable scenarios:**

- Creating `.gitlab-ci.yml` for new projects
- Reviewing existing `.gitlab-ci.yml`
- Optimizing CI/CD pipeline performance and maintainability

**Creation mode**: Confirm project tech stack and deployment approach → generate configuration based on rules below → self-check against all rules.

**Review mode**: Read `.gitlab-ci.yml` and files referenced by `include:` → check against rules item by item (annotate ID) → output report:

- **Must Fix**: Violates mandatory rules
- **Suggested Improvement**: Does not follow best practices
- **Optional Optimization**: Further optimization opportunity

## Company Standards

### Runner Tag Convention

| Tag | Purpose |
|-----|------|
| `sonar-scanner` | General CI tasks |

Set uniformly via `default.tags`:

```yaml
default:
  tags:
    - sonar-scanner
```

### Docker Image Convention

Manage image versions uniformly via top-level `variables:`; hard-coding in jobs is prohibited:

```yaml
variables:
  PYTHON_IMAGE: python:3.11-slim
  NODE_IMAGE: node:20-slim
  GO_IMAGE: golang:1.22-alpine
```

### ArgoCD GitOps Integration

CI is only responsible for Build & Test & Publish; deployment is triggered via ArgoCD GitOps:

- CI builds image → pushes to Registry → updates image tag in GitOps repo
- ArgoCD watches GitOps repo changes → auto-syncs to cluster
- Preview environments: MR branches auto-create temporary namespaces, destroyed after merge

**Red line**: Directly running `kubectl apply` / `helm install` to production environments from CI is prohibited.

## Rules

### DRY (Don't Repeat Yourself)

**D1: `default:` for shared configuration**

`tags`, `image`, `interruptible`, `retry`, and other cross-job shared configuration must go in `default:`; repeating in each job is prohibited.

**D2: `extends:` to eliminate job duplication**

When multiple jobs share the same configuration, extract a hidden job (`.job-name`) as a base class; child jobs inherit via `extends:`.

**D3: YAML anchors to reuse data blocks**

Use YAML anchors (`&anchor` / `*anchor`) for duplicated pure data (such as `rules:` condition lists).

**D4: `!reference` for selective reuse**

When only a specific property of a job needs reuse (not the entire job), use `!reference [.job, attribute]`.

### SSOT (Single Source of Truth)

**S1: `include:` to reference shared templates**

Company-level CI templates must be referenced from `your-org/ci-templates` via `include:project:`; copy-pasting is prohibited:

```yaml
include:
  - project: your-org/ci-templates
    ref: main
    file:
      - /.gitlab-ci/jobs/mr-doc-check.yml
```

**S2: `variables:` for centralized mutable values**

Image versions, service names, regions, and other mutable values must be defined as top-level `variables:`; hard-coding in `script:` is prohibited.

**S3: `workflow:rules:` for unified pipeline trigger strategy**

Use `workflow:rules:` at the top of the file to define when to create pipelines, avoiding each job defining redundant trigger conditions separately.

### Structure and Modern Syntax

| ID | Rule | Severity |
|----|------|--------|
| R1 | Use `rules:` instead of `only:/except:` (deprecated) | Must Fix |
| R2 | Use `needs:` to build DAG and reduce pipeline time | Suggested |
| R3 | Define `workflow:rules:` to avoid duplicate pipelines | Suggested |
| R4 | `stages:` order is logical (lint → build → test → publish → deploy) | Suggested |

### Reliability

| ID | Rule | Severity |
|----|------|--------|
| R5 | All jobs set reasonable `timeout:` | Suggested |
| R6 | Network-dependent jobs configure `retry:` + `when:` conditions | Suggested |
| R7 | Non-deployment jobs set `interruptible: true` | Suggested |
| R8 | Jobs requiring resource cleanup use `after_script:` | Optional |

### Security

| ID | Rule | Severity |
|----|------|--------|
| R9 | No hard-coded secrets/credentials in yml | Must Fix |
| R10 | Sensitive variables use CI/CD Variables (masked + protected) | Must Fix |
| R11 | Production deployment jobs restricted to `protected` branches/tags | Must Fix |

### Performance

| ID | Rule | Severity |
|----|------|--------|
| R12 | `artifacts:` set `expire_in:` to prevent storage bloat | Suggested |
| R13 | `cache:` configured with correct `key:` and `policy:` | Suggested |
| R14 | Large test suites use `parallel:` for sharding | Optional |
| R15 | Deployment jobs use `resource_group:` to prevent concurrent conflicts | Suggested |

## Examples

### Bad

#### 1. Violating DRY — Extensive configuration duplication

```yaml
build-frontend:
  stage: build
  image: node:20-slim
  tags:
    - sonar-scanner
  script:
    - npm ci
    - npm run build
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

build-backend:
  stage: build
  image: golang:1.22-alpine
  tags:
    - sonar-scanner
  script:
    - go build ./...
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

test-frontend:
  stage: test
  image: node:20-slim
  tags:
    - sonar-scanner
  script:
    - npm test
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

**Issues**: `tags` repeated 3 times (violates D1), `rules` repeated 3 times (violates D3), images hard-coded (violates S2).

#### 2. Deprecated syntax + direct deployment

```yaml
deploy:
  stage: deploy
  only:
    - main
  script:
    - kubectl apply -f k8s/ --kubeconfig /tmp/kubeconfig
  variables:
    IMAGE: registry.example.com/my-service:latest
```

**Issues**: Uses `only:` deprecated syntax (R1), directly runs `kubectl apply` to the cluster (ArgoCD red line), `latest` tag is not traceable (S2).

#### 3. Copy-paste templates

```yaml
# Copied lint configuration from another project
lint:
  stage: lint
  image: golangci/golangci-lint:v1.55
  script:
    - golangci-lint run
  tags:
    - sonar-scanner
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  allow_failure: true
  # 30 lines of identical configuration repeated across 5 projects...
```

**Issues**: Should be extracted to `your-org/ci-templates` (violates S1); cross-project maintenance cost is high, changes require 5 modifications.

### Good

#### 1. DRY + SSOT Standard Approach

```yaml
variables:
  NODE_IMAGE: node:20-slim
  GO_IMAGE: golang:1.22-alpine

default:
  tags:
    - sonar-scanner
  interruptible: true
  retry:
    max: 2
    when:
      - runner_system_failure

workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

.mr-only:
  rules: &mr-rules
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

include:
  - project: your-org/ci-templates
    ref: main
    file:
      - /.gitlab-ci/jobs/mr-doc-check.yml

stages:
  - build
  - test
  - publish

build-frontend:
  stage: build
  image: $NODE_IMAGE
  rules: *mr-rules
  script:
    - npm ci
    - npm run build
  artifacts:
    paths: [dist/]
    expire_in: 1 day

build-backend:
  stage: build
  image: $GO_IMAGE
  rules: *mr-rules
  script:
    - go build ./...

test-frontend:
  stage: test
  image: $NODE_IMAGE
  rules: *mr-rules
  needs: [build-frontend]
  script:
    - npm test
  coverage: '/coverage: \d+\.\d+%/'
```

**Strengths**:

- `default:` unifies tags/retry/interruptible (D1)
- YAML anchor `&mr-rules` reuses trigger conditions (D3)
- `variables:` manages image versions (S2)
- `include:` references company templates (S1)
- `workflow:rules:` unifies trigger strategy (S3)
- `needs:` accelerates DAG (R2)
- `artifacts:expire_in:` controls storage (R12)

#### 2. ArgoCD GitOps Integration

```yaml
publish:
  stage: publish
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

gitops-update:
  stage: deploy
  image: alpine/git:latest
  script:
    - git clone https://gitlab-ci-token:${GITOPS_TOKEN}@gitlab.example.com/your-org/gitops.git
    - cd gitops/apps/my-service
    - "sed -i 's|image:.*|image: ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA}|' values.yaml"
    - git commit -am "chore: update my-service to ${CI_COMMIT_SHA}"
    - git push
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  resource_group: production
```

**Strengths**: CI only builds and pushes images; deployment is triggered by updating the GitOps repo for ArgoCD (separation of concerns). `$CI_COMMIT_SHA` ensures image traceability. `resource_group:` prevents concurrent deployments (R15).

## Exemptions

| Scenario | Condition |
|------|------|
| Minimal project | Only lint/test with no deployment needs — ArgoCD integration may be omitted |
| Legacy project migration | `only:/except:` may be temporarily retained during migration; a migration plan is required |
| One-off scripts | Temporary CI jobs may be simplified; must annotate `# TODO: cleanup` |

## References

- [GitLab CI/CD YAML syntax reference](https://docs.gitlab.com/ee/ci/yaml/)
- [GitLab CI/CD pipeline efficiency](https://docs.gitlab.com/ee/ci/pipelines/pipeline_efficiency.html)
- [GitLab CI/CD `rules:` keyword](https://docs.gitlab.com/ee/ci/yaml/#rules)
- [GitLab CI/CD `needs:` keyword](https://docs.gitlab.com/ee/ci/yaml/#needs)
- [GitLab CI/CD `include:` keyword](https://docs.gitlab.com/ee/ci/yaml/#include)
