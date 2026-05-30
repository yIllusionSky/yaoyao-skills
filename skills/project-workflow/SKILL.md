---
name: project-workflow
description: 规划和执行本地仓库中的多项目任务编排。Use when the user asks to 拆分复杂开发任务、维护 develop/.workflow/<task-id>/ 任务记录、使用 detached worktree 隔离项目实现、分派 subagent 实现、发起 review、将项目分支 merge 到 develop，并完成最终验收和 commit。
---

# Project Workflow

用于规划和执行本地项目任务编排。除固定技术词、命令、文件名、workspace、subagent 外，使用中文。

## 触发后动作

1. 判断当前角色：main agent 或 implementation subagent。
2. main agent 必须读取 [main agent flow](./references/main-agent-flow.md) 和 [task format](./references/task-format.md)。
3. implementation subagent 必须读取 [subagent flow](./references/subagent-flow.md) 和 [task format](./references/task-format.md)。
4. 如果当前环境不能启动 subagent，则按同一协议顺序执行，并在对应 `log.md` 说明。
5. 触发后严格按对应 reference 的工作流程执行。

## 角色

- main agent：拆分任务、维护根记录、准备 worktree、分派 subagent、merge 项目分支到 `develop`、最终验收和 commit。
- implementation subagent：只在指定 `project-worktree` 内实现、自测、更新项目任务记录，并在自测通过后提交项目分支 commit。

## 参考文件

- 文件格式看 [task format](./references/task-format.md)。
- 主流程看 [main agent flow](./references/main-agent-flow.md)。
- 子 agent 看 [subagent flow](./references/subagent-flow.md)。
