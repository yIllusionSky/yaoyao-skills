---
name: project-workflow
description: 本地项目任务编排技能。用于维护 develop/.workflow/<task-id>/ 任务记录、detached worktree、subagent 实现、review、集成和总体验收闭环。
---

# Project Workflow

用于规划和执行本地项目任务编排。除固定技术词、命令、文件名、workspace、subagent 外，使用中文。

任务记录目录固定为 `develop/.workflow/<task-id>/`。

## References

- 创建或维护任务文件、日志文件时，读取 [task format](./references/task-format.md)。
- 编排完整任务时，读取 [main agent flow](./references/main-agent-flow.md)。
- 启动或执行 subagent 任务时，读取 [subagent flow](./references/subagent-flow.md)。
