---
name: project-workflow
description: 规划和执行本地仓库中的多项目任务编排。Use when the user asks to 拆分复杂开发任务、维护 develop/.workflow/<task-id>/ 任务记录、使用 detached worktree 隔离项目实现、分派 subagent 实现、将项目分支 merge 到 develop、发起总体验收 review，并完成最终 commit。
---

# Project Workflow

用于规划和执行本地项目任务编排。除固定技术词、命令、文件名、workspace、subagent 外，使用中文。

## 触发后动作

1. 判断当前角色：main agent 或 implementation subagent。
2. 必须读取 [task format](./references/task-format.md)。
3. main agent 必须读取 [main agent flow](./references/main-agent-flow.md)，并严格按 main agent flow 执行。
4. implementation subagent 必须读取 [subagent flow](./references/subagent-flow.md)，并严格按 subagent flow 执行。
5. 如果当前环境不能启动 subagent，则由 main agent 按同一协议顺序执行，并在对应 `log.md` 说明。

## 角色

- main agent：拆分任务、维护根记录、准备 worktree、分派 subagent、merge 项目分支到 `develop`、最终验收和 commit。
- implementation subagent：只在指定 `project-worktree` 内实现、自测、更新项目任务记录，并提交项目分支 commit。
