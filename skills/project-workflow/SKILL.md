---
name: project-workflow
description: 以本地 main 分支为基线和最终集成目标，使用独立 worktree、implementation subagent 和 review subagent 编排 monorepo 多项目任务。仅在用户明确要求使用 project-workflow 时使用。
---

# Project Workflow

用于规划和执行本地 monorepo 多项目任务编排。除固定技术词、命令、文件名、workspace、subagent 外，使用中文。

## 触发后动作

1. 判断当前角色：main agent、implementation subagent 或 review subagent。
2. 必须读取 [workspace layout](./references/workspace-layout.md) 和 [task format](./references/task-format.md)。
3. main agent 读取 [projects](./references/projects.md)，按 [main agent flow](./references/main-agent-flow.md) 编排、集成并合并回本地 `main`。
4. implementation subagent 按 [implementation subagent flow](./references/implementation-subagent-flow.md) 在指定 worktree 实现、自测和提交。
5. review subagent 按 [review subagent flow](./references/review-subagent-flow.md) 只读审查指定版本，输出 findings。
6. 生成或审查 commit 时必须使用 `git-workflow`；本 skill 只定义提交时机和角色职责。

## 执行范围

- 只处理当前任务及授权路径；调用其他 skill 时继承本次任务范围。
- 子代理可正常安装依赖，但不提交根 `Cargo.lock` 和 `bun.lock`。主代理在集成安装和测试时更新并提交锁文件。

除安装自动生成的根锁文件外，implementation subagent 的文件修改仍须符合 `Allowed Paths`；需要额外路径时交由 main agent 在用户任务范围内协调。
