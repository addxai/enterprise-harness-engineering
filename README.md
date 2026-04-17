[中文](README.zh-CN.md) | English

# Enterprise Harness Engineering

**Enterprise-grade AI Agent Skills for software development, DevOps, SRE, security, and product teams.**

---

Over the past year, almost every company has been "using AI" -- adopting Cursor, Claude Code, running a few training sessions. Yet the results rarely match expectations.

The problem is not that AI is not powerful enough. **The problem is that your enterprise was not designed for AI.**

An enterprise needs to cross three chasms to be truly AI-driven:

- **Human habits.** The more experienced people are, the more they default to "is this really allowed?" instead of "why not?"
- **Tool interfaces.** Most internal tools are GUI-only -- designed for humans clicking buttons. AI calls APIs. No API means AI cannot operate, and entire departments are excluded from AI transformation.
- **Organizational structure.** Assembly-line dependencies -- I finish then hand off to you, you finish then hand off to the next person. Every extra person in the loop is another blocking point.

The root cause is the same: **existing enterprises are designed for human-to-human collaboration, not human-to-AI collaboration.**

Giving everyone a chainsaw but keeping the factory designed for handsaws -- workstations too small, voltage too low, assembly line unchanged -- gets you 1.2x, not 10x.

**10x is easier than 2x.** 2x means optimizing within the old framework. 10x means adopting a new one. Enterprise Harness Engineering is that new framework.

---

## What is Enterprise Harness Engineering

Harness Engineering has become a popular concept in the tech community -- building feedback loops, testing frameworks, and runtime environments for AI Agents so they can autonomously verify and deliver code. This is right, but it only solves part of the problem.

**Enterprise Harness Engineering extends Harness Engineering to the enterprise level.** It is not just about building feedback loops for AI coding agents -- it is about making every layer of the enterprise AI-accessible:

- Can the **technology** be AI-harnessed? Does the code have closed-loop feedback? Can AI autonomously verify and deliver?
- Can the **tools** be AI-harnessed? Do internal systems have APIs? Can AI operate them directly?

The core formula:

> **Enterprise AI Readiness = Tech Loop x Tool API**

This is **multiplication**, not addition. If either dimension is zero, the total is zero:

| Missing | Symptom | Result |
|---------|---------|--------|
| Tech Harness | AI writes code but nobody knows if it is correct | No real productivity gain; extra review burden instead |
| Tool Harness | R&D uses AI but other departments are still clicking buttons | AI adoption stays confined to engineering |

Most companies have only addressed a fraction of the tech layer. Tool layer remains untouched. The result: 1.2x, not 10x.

---

## Harness Architecture

### The 4-Layer Stack: Human -> Agent -> Skill -> Tool

```
+----------------------------------------------------------+
|                   Human (Judgment & Decision)             |
|                                                          |
|  Provides intent, business context, final decisions      |
|  No need to remember Skill names -- describe in          |
|  natural language what you want to do                    |
+----------------------------+-----------------------------+
                             | Natural Language
+----------------------------v-----------------------------+
|                   Coding Agent Layer                      |
|                                                          |
|  Claude Code / Cursor / OpenClaw                         |
|  - Understand intent -> select Skill -> orchestrate      |
|  - Multi-Skill composition, cross-department calls       |
|  - Same Agent + different Skills = different roles       |
+----------------------------+-----------------------------+
                             | Invocation
+----------------------------v-----------------------------+
|                      Skill Layer                          |
|                                                          |
|  ~100 Skills across 6 departments                        |
|  - Each Skill is a Markdown document                     |
|  - Encodes expert experience: triggers, steps, rules     |
|  - Everything as Code: Git-managed, Code Review enforced |
+----------------------------+-----------------------------+
                             | Operation
+----------------------------v-----------------------------+
|                       Tool Layer                          |
|                                                          |
|  SaaS -- Collaboration / Dev (GitLab, Sentry) /          |
|          Data (DataHub, Superset) / Ops (Grafana, K8s)   |
|  Internal Platforms -- IoT platform / Test automation     |
|  Hardware Toolchain -- Firmware build / Instruments       |
+----------------------------------------------------------+
```

Each layer has a clear purpose:

**Tool Layer -- Everything as Code or SaaS. Eliminate manual operations.** All tools must be SaaS or API-accessible. All operations must be codified. Infrastructure uses Terraform (IaC), deployments use ArgoCD (GitOps), secrets use Vault, CI uses GitLab Pipeline. Nobody clicks buttons in a console. Nobody runs scripts locally. **Everything as Code or Data -- manual operations are the enemy of AI closed loops.** Only when all state is API-queryable and all changes have audit trails can AI Agents see the full context.

**Skill Layer -- Encode expert knowledge into AI-executable workflows.** Skills are not just API documentation. They encode how senior experts think -- how they judge, how they decide, what rules they follow -- into Markdown. Skills are the crystallization of professional knowledge. Once encoded, an employee's core expertise can be executed in parallel by AI, amplified infinitely through tokens.

**Coding Agent Layer -- Unified entry point, free orchestration.** No need to build a specialized bot for every scenario. The same Coding Agent, loaded with different Skills, becomes different roles. And it can natively write code -- when it finds a bug, it does not just notify someone; it reads the source, writes the fix, and submits a merge request.

### Skill: Not API Docs, but Organizational Muscle Memory

A Skill does not just tell AI "how to call this API." It encodes a senior expert's entire judgment framework:

- A **VOC Analysis Skill** does not just call APIs to scrape data -- it encodes how a senior product manager reads reviews, identifies trends, and benchmarks against competitors.
- A **WiFi Tuning Skill** does not just control instruments -- it encodes how an RF engineer selects initial parameters, judges convergence direction, and defines pass/fail criteria.
- An **SRE Alert Handling Skill** does not just read Grafana metrics -- it encodes how an on-call engineer triages, identifies root causes, and decides when to scale vs. when to rollback.

The old model: `Human Skill x Time = Output` -- one person, 8 hours a day.

The new model: **`Professional Knowledge x Token = Output`** -- the same expertise executed in parallel by AI, amplified infinitely, no longer bounded by human time. **Skills are the crystallization of knowledge. AI is the amplifier.**

---

## Agent Personas: One Agent, Many Roles

The same Coding Agent, loaded with different Skill combinations, becomes a different Agent Persona:

| Persona | Domain | Core Skill Stack | Typical Workflow |
|---------|--------|-----------------|------------------|
| **Software R&D Agent** | Software Dev | dev-workflow + architect + gitlab-mr + testing-strategy | Requirement -> Design -> Code -> Test -> MR -> Deploy (9-step loop) |
| **SRE Agent** | Operations | sre-agent + prometheus + k8s-ops + grafana + argocd | Alert -> Triage -> Root Cause -> Fix -> Notification |
| **Data Agent** | Data Analytics | datahub-schema-search + superset + dagster | "Last week's DAU trend" -> Find table -> SQL -> Chart -> Report |
| **Customer Support Agent** | Customer Success | troubleshooting + cs-workspace + sla-alert-analysis | Device offline -> Log search -> Root cause -> Diagnosis report -> Update ticket |
| **Product Agent** | Product Planning | voc-analysis + market-analysis + story-craftsman | VOC scraping -> Sentiment analysis -> Competitive comparison -> Trend report |
| **BSP/HW Agent** | Hardware Dev | firmware-build + embed-ci-setup + instrument-ops | Tune params -> Flash firmware -> Measure -> Analyze -> Iterate until pass |

**Personas are not independent Agent services -- they are working modes of the Coding Agent.** Switch the Skill set, switch the role. No deployment, no integration, no maintenance.

---

## Why Not Traditional Specialized Agents

Many companies build specialized AI Agents using LangChain/LangGraph -- hardcoded workflows, independent services. We chose a fundamentally different approach:

| | Traditional Specialized Agent | Coding Agent + Skills |
|---|---|---|
| **Architecture** | One independent service per scenario, dedicated code, dedicated deployment | One universal Coding Agent, Skills are Markdown docs |
| **Capability boundary** | Can only do one thing; workflow is hardcoded | Free cross-department composition -- SRE scenario can call the data team's `superset` |
| **Extension cost** | New scenario = write code + deploy + maintain | New scenario = write a Markdown document |
| **Who maintains** | Requires AI engineers | Domain experts write Skills themselves |
| **Cross-scenario collaboration** | Agents need integration protocols | Same Agent, natively cross-scenario |
| **Repair capability** | Can only diagnose and notify | Can read source, write fix, submit MR -- because it IS a Coding Agent |

The last row is the decisive advantage: **a Coding Agent can natively write code.** A traditional SRE Agent that finds a bug can only notify a human. A Coding Agent can read the source, write the fix, run tests, and submit a merge request. Skills tell it how to find the problem; once found, it inherently has the ability to fix it. This is not "AI-assisted" -- it is "AI end-to-end closed loop."

---

## Core Principles

| Principle | One-line Explanation |
|-----------|---------------------|
| **Agent-First** | Coding Agent is the unified entry point for all AI workflows. Human -> Agent -> Tool, not Human -> GUI -> Tool |
| **Skill as Knowledge** | Professional knowledge encoded as Skills, executed in parallel by AI, amplified infinitely through Tokens |
| **Everything as Code** | Skills, Agent config, Hooks -- all version-controlled, Code Review enforced, traceable and rollback-able |
| **Unified Observability** | Observable means actionable -- if the Agent can see the data, it can analyze, decide, and act |
| **Source of Truth in SaaS** | No separate knowledge bases. Pull data directly from existing systems. Collaboration platform = docs, data catalog = schemas, code repo = code |
| **No AI-Opaque GUI** | Never build GUI-only tools that AI cannot operate. Every tool must have a CLI or API entry point |

These principles share a common direction: **make AI a first-class citizen.** Every system, every data source, every tool in the enterprise must be visible, operable, and verifiable by AI.

---

## Skills Catalog

25 Skills across 6 categories:

### Software Development

| Skill | Description |
|-------|-------------|
| [architect](skills/architect/) | Architecture design through Socratic questioning, producing structured technical documents |
| [dev-workflow](skills/dev-workflow/) | 9-step development lifecycle orchestrator from User Story to CD |
| [story-craftsman](skills/story-craftsman/) | Guided interview to produce structured User Stories |
| [doc-writing](skills/doc-writing/) | HWPR/AWOR framework separating human judgment from AI expansion |
| [testing-strategy](skills/testing-strategy/) | Layered testing architecture (L1-L4) with TDD workflow |
| [code-review](skills/code-review/) | AI-driven code review with standards compliance |
| [code-submit](skills/code-submit/) | Cross-platform code submission: lint, review, stage, commit, MR |
| [uat-story-writer](skills/uat-story-writer/) | Discover missing UAT scenarios and generate Gherkin test cases |
| [multi-worktree-dev](skills/multi-worktree-dev/) | Parallel development with git worktree isolation |
| [mock-engine](skills/mock-engine/) | Local mock infrastructure management (Docker Compose stack) |
| [embed-ci-setup](skills/embed-ci-setup/) | Embedded C project CI pipeline with SonarQube scanning |
| [clean-cache](skills/clean-cache/) | Batch scan and clean Flutter/Android/iOS/Node.js project caches |

### GitLab Integration

| Skill | Description |
|-------|-------------|
| [gitlab-ci](skills/gitlab-ci/) | GitLab CI pipeline design and optimization (15 best-practice rules) |
| [gitlab-mr](skills/gitlab-mr/) | Drive MR from creation to mergeable state (CI green + no conflicts) |

### Monitoring & Observability

| Skill | Description |
|-------|-------------|
| [sentry](skills/sentry/) | Error tracking, crash analysis, and release health monitoring |
| [sentry-onboarding](skills/sentry-onboarding/) | Create and configure Sentry projects across environments |
| [grafana](skills/grafana/) | Query and manage Grafana dashboards, alerts, and data sources |
| [prometheus](skills/prometheus/) | Construct PromQL queries and analyze metrics |
| [k8s-ops](skills/k8s-ops/) | Multi-cluster Kubernetes resource management and troubleshooting |

### SRE & Operations

| Skill | Description |
|-------|-------------|
| [sre-agent](skills/sre-agent/) | SRE intelligence: oncall triage, root cause analysis, patrol, self-improvement |

### Security & Compliance

| Skill | Description |
|-------|-------------|
| [terraform-audit](skills/terraform-audit/) | IaC audit across security, cost, quality, and architecture |
| [security-compliance-review](skills/security-compliance-review/) | Structured security and compliance review framework |
| [local-security-check](skills/local-security-check/) | Check Skill files for security risks and prompt injection |
| [trufflehog-cli](skills/trufflehog-cli/) | Secret scanning with TruffleHog CLI |

### Market Research

| Skill | Description |
|-------|-------------|
| [voc-analysis](skills/voc-analysis/) | Multi-platform Voice of Customer analysis and competitive intelligence |

---

## Installation

All skills follow the Agent Skills Specification, compatible with 30+ AI coding agents.

### Claude Code (Plugin Marketplace)

```bash
# Install as a plugin (recommended)
/plugin marketplace add addxai/enterprise-harness-engineering

# Then install specific skills
/plugin install enterprise-harness-engineering
```

### Cursor

```bash
# Clone and copy skills to your project
git clone https://github.com/addxai/enterprise-harness-engineering.git
cp -r enterprise-harness-engineering/skills/* .cursor/skills/

# Or install globally
cp -r enterprise-harness-engineering/skills/* ~/.cursor/skills/
```

You can also add individual skills via **Settings > Rules > Add Rule > Remote Rule** and point to a skill directory on GitHub.

### Windsurf

```bash
git clone https://github.com/addxai/enterprise-harness-engineering.git
cp -r enterprise-harness-engineering/skills/* .windsurf/skills/

# Or install globally
cp -r enterprise-harness-engineering/skills/* ~/.codeium/windsurf/skills/
```

### Universal (.agents/skills/) -- GitHub Copilot, Gemini CLI, Codex, Kiro, Junie, and more

```bash
git clone https://github.com/addxai/enterprise-harness-engineering.git
cp -r enterprise-harness-engineering/skills/* .agents/skills/

# Or install globally
cp -r enterprise-harness-engineering/skills/* ~/.agents/skills/
```

### Install a Single Skill

```bash
# Example: install only the sre-agent skill
git clone --depth 1 https://github.com/addxai/enterprise-harness-engineering.git
cp -r enterprise-harness-engineering/skills/sre-agent .claude/skills/
```

### Supported Platforms

| Platform | Project-level Path | Global Path |
|----------|-------------------|-------------|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| GitHub Copilot | `.agents/skills/` | `~/.agents/skills/` |
| Gemini CLI | `.agents/skills/` | `~/.agents/skills/` |
| OpenAI Codex | `.agents/skills/` | `~/.agents/skills/` |
| Kiro (AWS) | `.agents/skills/` | `~/.agents/skills/` |
| Junie (JetBrains) | `.agents/skills/` | `~/.agents/skills/` |
| Goose (Block) | `.agents/skills/` | `~/.agents/skills/` |
| Roo Code | `.agents/skills/` | `~/.agents/skills/` |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new Skills or improving existing ones.

The short version:

1. Fork this repository
2. Create a skill directory under `skills/`
3. Add a `SKILL.md` with proper frontmatter (`name` and `description` in YAML frontmatter)
4. Submit a merge request

---

## About

Built by [AddX.ai (积加科技)](https://addx.ai) — an AI-first engineering organization practicing Enterprise Harness Engineering at scale.

---

## License

[Apache-2.0](LICENSE)
