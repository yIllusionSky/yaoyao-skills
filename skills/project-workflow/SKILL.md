---
name: project-workflow
description: 本地 monorepo 多项目任务编排技能。仅在用户明确要求使用 project-workflow 时使用。
---

# Project Workflow

用于规划和执行本地 monorepo 多项目任务编排。除固定技术词、命令、文件名、workspace、subagent 外，使用中文。

## 触发后动作

1. 判断当前角色：main agent、implementation subagent 或 review subagent。
2. 必须读取 [workspace layout](./references/workspace-layout.md)、[task format](./references/task-format.md) 和 [commit](./references/commit.md)。
3. main agent 必须读取 [main agent flow](./references/main-agent-flow.md)，并严格按 main agent flow 执行。
4. implementation subagent 必须读取 [implementation subagent flow](./references/implementation-subagent-flow.md)，并严格按 implementation subagent flow 执行。
5. review subagent 必须读取 [review subagent flow](./references/review-subagent-flow.md)，并严格按 review subagent flow 执行。

## 角色

- main agent：拆分任务、维护根记录、准备 worktree、分派 subagent、merge 项目分支到 `develop/` 的 `<task-id>` 分支、最终验收和 commit。
- implementation subagent：只在指定 `project-worktree` 内实现、自测、更新项目任务记录，并提交项目分支 commit。
- review subagent：只审查 `develop/` 当前 `<task-id>` 分支状态，输出 review findings，不直接修改文件。

执行命令时如缺少项目依赖，在当前职责允许的工作目录内自行安装后继续。

本 skill 中的 commit 统一遵守 [commit](./references/commit.md)；同时使用其他 skill 时，不继承其他 skill 的 commit 格式或 commit 前置检查。
