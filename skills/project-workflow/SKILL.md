---
name: project-workflow
description: 以本地 main 分支为基线和最终集成目标，使用独立 worktree、implementation subagent 和 review subagent 编排 monorepo 多项目任务。仅在用户明确要求使用 project-workflow 时使用。
---

# Project Workflow

用于规划和执行本地 monorepo 多项目任务编排。除固定技术词、命令、文件名、workspace、subagent 外，使用中文。

## 触发后动作

1. 判断当前角色：main agent、implementation subagent 或 review subagent。
2. 必须读取 [workspace layout](./references/workspace-layout.md) 和 [task format](./references/task-format.md)。
3. main agent 必须读取 [projects](./references/projects.md) 和 [main agent flow](./references/main-agent-flow.md)，并严格按 main agent flow 执行。
4. implementation subagent 必须读取 [implementation subagent flow](./references/implementation-subagent-flow.md)，并严格按 implementation subagent flow 执行。
5. review subagent 必须读取 [review subagent flow](./references/review-subagent-flow.md)，并严格按 review subagent flow 执行。
6. 生成或审查 commit 时必须使用 `git-workflow`；本 skill 只定义提交时机和角色职责。

## 角色

- main agent：拆分任务、维护根记录、准备 worktree、分批分派 subagent、merge 项目分支到 `develop/` 的 `<task-id>` 分支、最终验收并将任务分支 merge 回本地 `main`。
- implementation subagent：只在指定 `project-worktree` 内实现、自测、更新项目任务记录，并提交项目分支 commit。
- review subagent：只审查 `develop/` 当前 `<task-id>` 分支状态，输出 review findings，不直接修改文件。

执行命令时如缺少项目依赖，可以在当前职责允许的工作目录内安装；安装产生的 tracked 修改仍须符合 `Allowed Paths`，否则返回 main agent 扩展授权或处理。
