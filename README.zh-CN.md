中文 | [English](README.md)

# Enterprise Harness Engineering

**企业级 AI Agent Skills，覆盖软件研发、DevOps、SRE、安全和产品团队。**

## 什么是 Enterprise Harness Engineering？

几乎每家公司都在"用 AI"——上了 Cursor、用了 Claude Code，做了几场培训。效果远不及预期。问题不是 AI 不够强，**问题是你的企业不是为 AI 设计的。**

Enterprise Harness Engineering 将 Harness Engineering 的概念从技术层扩展到企业级。不只是为 AI 编码 Agent 搭建反馈闭环，而是让企业的每一层都能被 AI 驱动：

- **技术**能不能被 AI harness？代码有没有闭环，AI 能不能自主验证和交付？
- **工具**能不能被 AI harness？内部系统有没有 API，AI 能不能直接操作？

### 核心公式

> **企业 AI 化程度 = 技术闭环 x 工具接口化**

这是**乘法**，不是加法。任何一个维度为零，整体为零：

| 缺什么 | 表现 | 结果 |
|--------|------|------|
| 缺技术 Harness | AI 写了代码但没人知道对不对 | 产研效率没有实质提升，反而多了 review 负担 |
| 缺工具 Harness | 产研用上了 AI，其他部门还在点按钮 | AI 化局限于工程团队 |

## Harness 架构

三层技术栈：**人 -> Agent -> Skill -> Tool**

```
+----------------------------------------------------------+
|                    人（判断与决策）                          |
|                                                          |
|  提供意图、业务上下文、最终决策                               |
|  不需要记住 Skill 名字，用自然语言描述想做什么                  |
+----------------------------+-----------------------------+
                             | 自然语言
+----------------------------v-----------------------------+
|                   Coding Agent Layer                     |
|                                                          |
|  Claude Code / Cursor / OpenClaw                         |
|  - 理解意图 -> 选择 Skill -> 编排执行                      |
|  - 多 Skill 组合、跨部门调用                                |
|  - 同一个 Agent，加载不同 Skill = 不同角色                   |
+----------------------------+-----------------------------+
                             | 调用
+----------------------------v-----------------------------+
|                      Skill Layer                         |
|                                                          |
|  ~100 个 Skill，覆盖 6+ 个部门                             |
|  - 每个 Skill 是一份 Markdown 文档                         |
|  - 编码了专家经验：触发条件、执行步骤、规则约束                 |
|  - Everything as Code：Git 管理，Code Review 强制           |
+----------------------------+-----------------------------+
                             | 操作
+----------------------------v-----------------------------+
|                       Tool Layer                         |
|                                                          |
|  SaaS -- 协同 / 研发 (GitLab, Sentry) /                  |
|          数据 (DataHub, Superset) / 运维 (Grafana, K8s)    |
|  内部平台 -- 自动化、测试、部署                               |
|  硬件工具链 -- 固件编译、仪器控制                             |
+----------------------------------------------------------+
```

### Tool Layer -- Everything as Code or SaaS，消灭手动操作

所有工具必须 SaaS 化或 API 化，所有操作必须代码化。基础设施用 Terraform（IaC），部署用 ArgoCD（GitOps），密钥用 Vault，CI 用 Pipeline。没有人在控制台点按钮，没有人在本地跑脚本。**Everything as Code or Data -- 手动操作是 AI 闭环的天敌。** 只有当所有状态都通过 API 可查、所有变更都有审计记录，AI Agent 才能看到完整的上下文。

### Skill Layer -- 把专家经验编码为 AI 可执行的工作流

Skill 不只是 API 文档，而是把资深专家"怎么判断、怎么决策、什么规则要遵守"的经验编码成 Markdown。Skill 是专业知识的沉淀，通过 AI 并行执行、用 Token 无限放大。

### Coding Agent Layer -- 统一入口，自由编排

不需要为每个场景搭一个专用 Bot。同一个 Coding Agent，加载不同 Skill，就变成不同角色。而且它天然能写代码——发现 bug 后不只是通知人，能直接读源码、写修复、跑测试、提 MR。

## Skill 即知识

> **专业知识 x Token = 产出**

以前是 `人的能力 x 时间 = 产出`，一个人一天只有 8 小时。

Skill 化之后，同一份专家经验可以被 AI 并行执行、无限放大，不再受人的时间限制。**Skill 是专业知识的沉淀，AI 是知识的放大器。**

## Agent Personas：一个 Agent，多个角色

同一个 Coding Agent，加载不同的 Skill 组合，就变成不同的 Agent Persona：

| Persona | 服务场景 | 核心 Skill 组合 | 典型工作流 |
|---------|---------|----------------|----------|
| **Software R&D Agent** | 软件研发 | dev-workflow + architect + gitlab-mr + testing-strategy | 需求 -> 设计 -> 编码 -> 测试 -> MR -> 部署，9 步闭环 |
| **SRE Agent** | 运维 | sre-agent + prometheus + k8s-ops + grafana | 告警 -> 分诊 -> 根因分析 -> 修复 -> 通知 |
| **Data Agent** | 数据分析 | datahub-schema-search + superset + dagster | "上周日活趋势" -> 找表 -> SQL -> 图表 -> 报告 |
| **Customer Support Agent** | 客户成功 | troubleshooting + sla-alert-analysis | 设备掉线 -> 日志检索 -> 根因定位 -> 诊断报告 -> 更新工单 |
| **Product Agent** | 产品规划 | voc-analysis + story-craftsman | VOC 爬取 -> 情感分析 -> 竞品对比 -> 趋势报告 |
| **Security Agent** | 安全合规 | security-compliance-review + terraform-audit + trufflehog-cli | 扫描 -> 检测 -> 分类 -> 修复 |

**Persona 不是独立的 Agent 服务，而是 Coding Agent 的工作模式。** 换一组 Skill 就换一个角色，不需要部署、不需要对接、不需要维护。

## 为什么不做传统的专用 Agent？

| | 传统专用 Agent | Coding Agent + Skills |
|---|---|---|
| **架构** | 每个场景一个独立服务，专用代码，专用部署 | 一个通用 Coding Agent，Skills 是 Markdown 文档 |
| **能力边界** | 只能做一件事，链路写死 | 跨部门自由组合 -- SRE 场景可以调数据团队的 `superset` |
| **扩展成本** | 新场景 = 写代码 + 部署 + 维护 | 新场景 = 写一份 Markdown 文档 |
| **谁来维护** | 需要 AI 工程师 | 业务专家自己就能写 Skill |
| **跨场景协作** | Agent 之间需要对接协议 | 同一个 Agent，天然跨场景 |
| **修复能力** | 只能诊断和通知 | 能直接读代码、写修复、提 MR -- 因为它本身就是 Coding Agent |

最后一行是决定性优势：**Coding Agent 天然能写代码。** 传统 SRE Agent 发现 bug 只能通知人。Coding Agent 发现 bug 后，可以直接读源码、写修复、跑测试、提 MR。这不是"AI 辅助"，是 **AI 端到端闭环**。

## 核心原则

| 原则 | 一句话解释 |
|------|----------|
| **Agent-First** | Coding Agent 是所有 AI 工作流的统一入口。人 -> Agent -> Tool，不是人 -> GUI -> Tool |
| **Skill as Knowledge** | 专业知识编码为 Skill，通过 AI 并行执行、用 Token 无限放大 |
| **Everything as Code** | Skill、Agent 配置、Hooks 全部版本控制，Code Review 强制，可追溯可回滚 |
| **Unified Observability** | 可观测即可闭环 -- Agent 能看到的数据，就能分析、决策、行动 |
| **Source of Truth in SaaS** | 不建独立知识库，从现有系统直接取数据。协同平台 = 文档，数据目录 = 表结构，代码仓库 = 代码 |
| **No AI-Opaque GUI** | 不做无法被 AI 操作的纯 GUI 工具。每个工具必须有 CLI 或 API 入口 |

## Skills 目录

### 软件研发

| Skill | 简介 |
|-------|------|
| [architect](skills/architect/) | 通过苏格拉底式提问驱动架构设计，输出结构化技术文档 |
| [dev-workflow](skills/dev-workflow/) | 从 User Story 到 CD 的 9 步研发全流程编排 |
| [story-craftsman](skills/story-craftsman/) | 引导式访谈生成结构化 User Story |
| [doc-writing](skills/doc-writing/) | HWPR/AWOR 框架：区分人的价值判断与 AI 扩写 |
| [testing-strategy](skills/testing-strategy/) | 分层测试架构（L1-L4）与 TDD 工作流 |
| [code-review](skills/code-review/) | AI 驱动的代码审查与标准合规检查 |
| [code-submit](skills/code-submit/) | 跨平台代码提交：lint、review、暂存、commit、MR |
| [uat-story-writer](skills/uat-story-writer/) | 发现缺失的 UAT 场景并生成 Gherkin 测试用例 |
| [multi-worktree-dev](skills/multi-worktree-dev/) | 基于 git worktree 的并行开发隔离方案 |
| [mock-engine](skills/mock-engine/) | 本地 Mock 基础设施管理（Docker Compose 栈） |
| [embed-ci-setup](skills/embed-ci-setup/) | 嵌入式 C 项目 CI Pipeline 与 SonarQube 扫描 |
| [clean-cache](skills/clean-cache/) | 批量扫描清理构建缓存（Flutter/Android/iOS/Node.js），释放磁盘空间 |

### GitLab 集成

| Skill | 简介 |
|-------|------|
| [gitlab-ci](skills/gitlab-ci/) | GitLab CI Pipeline 设计与优化（15 条最佳实践） |
| [gitlab-mr](skills/gitlab-mr/) | 驱动 MR 从创建到可合并（CI 绿 + 无冲突） |

### 监控与可观测性

| Skill | 简介 |
|-------|------|
| [sentry](skills/sentry/) | 错误追踪、崩溃分析与发布健康度监控 |
| [sentry-onboarding](skills/sentry-onboarding/) | 跨环境创建和配置 Sentry 项目 |
| [grafana](skills/grafana/) | Grafana 面板、告警和数据源的查询与管理 |
| [prometheus](skills/prometheus/) | PromQL 查询构造与指标分析 |
| [k8s-ops](skills/k8s-ops/) | 多集群 Kubernetes 资源管理与故障排查 |

### SRE 与运维

| Skill | 简介 |
|-------|------|
| [sre-agent](skills/sre-agent/) | SRE 智能体：oncall 分诊、根因分析、预防巡检、自我改进 |

### 安全与合规

| Skill | 简介 |
|-------|------|
| [terraform-audit](skills/terraform-audit/) | IaC 审计：安全、成本、质量、架构四维检查 |
| [security-compliance-review](skills/security-compliance-review/) | 结构化安全与合规审查框架 |
| [local-security-check](skills/local-security-check/) | Skill 文件安全检查与 prompt 注入检测 |
| [trufflehog-cli](skills/trufflehog-cli/) | TruffleHog CLI 密钥扫描 |

### 市场研究

| Skill | 简介 |
|-------|------|
| [voc-analysis](skills/voc-analysis/) | 多平台用户之声（VOC）分析与竞争情报 |

## 安装

所有 Skill 遵循 Agent Skills Specification，兼容 30+ AI 编程 Agent。

### Claude Code（插件市场）

```bash
/plugin marketplace add addxai/enterprise-harness-engineering
/plugin install enterprise-harness-engineering
```

### Cursor

```bash
git clone https://github.com/addxai/enterprise-harness-engineering.git
cp -r enterprise-harness-engineering/skills/* .cursor/skills/
```

### Windsurf

```bash
git clone https://github.com/addxai/enterprise-harness-engineering.git
cp -r enterprise-harness-engineering/skills/* .windsurf/skills/
```

### 通用安装（GitHub Copilot / Gemini CLI / Codex / Kiro / Junie 等）

```bash
git clone https://github.com/addxai/enterprise-harness-engineering.git
cp -r enterprise-harness-engineering/skills/* .agents/skills/
```

### 支持的平台

| 平台 | 项目级路径 | 全局路径 |
|------|-----------|---------|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| GitHub Copilot | `.agents/skills/` | `~/.agents/skills/` |
| Gemini CLI | `.agents/skills/` | `~/.agents/skills/` |
| OpenAI Codex | `.agents/skills/` | `~/.agents/skills/` |

## 参与贡献

参见 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何添加新 Skill 或改进现有 Skill。

## 关于

由 [积加科技 (AddX.ai)](https://addx.ai) 构建 — 一个在企业级规模实践 Harness Engineering 的 AI-first 工程组织。

## 许可证

[Apache-2.0](LICENSE)
