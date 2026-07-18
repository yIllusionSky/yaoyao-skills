# yaoyao-skills

一组用于统一项目协作规范的技能包。

该仓库提供简洁的中文项目规范，适合在 Codex、Copilot 或其他支持技能 / 提示词的工作流中复用，减少多人协作时格式和记录风格不一致的问题。

> [!NOTE]
> 本仓库内技能要求除固定关键词外尽量使用中文，不写提交人、协作者、工具来源或 AI 署名。

## Skills

- `git-workflow`: 规范 branch、commit、PR、issue 和 tag。
- `github-actions`: 规范 GitHub Actions CI、app / Docker / Tauri 的 tag release workflow，并提供可复制 assets 和复制脚本。
- `team-changelog`: 只在 tag/release 前根据 commit 区间整理 `CHANGELOG.md` 和 release notes，避免 commit/PR 阶段冲突。
- `changelog`: 持续维护 `[Unreleased]`，并在 tag 前审计和发布版本区块。
- `rust-architecture`: 规范 Rust CLI、library、后端服务和复杂应用的项目结构、架构边界、错误处理和测试规则。
- `project-docs`: 规范长期项目文档，包括根 README、子项目 README、架构文档、功能说明、手动测试和运行维护文档。
- `project-workflow`: 编排 workspace 布局、`.workflow/.projects` 显式项目拆分文件、`.workflow/<task-id>/` 本地任务记录、`develop/` 集成 worktree 目录、项目级 implementation subagent、review subagent、主集成和总体验收闭环。
- `team-project-workflow`: 在真实 `develop` 分支上执行同类多项目编排，并在验收后合并任务分支回 `develop`。

`changelog` 与 `team-changelog` 是互斥安装的两种 changelog 模式；`project-workflow` 与 `team-project-workflow` 也是互斥安装的两种任务编排模式。

## 项目目标

- 统一项目协作内容的书写格式
- 降低团队在提交描述上的沟通成本
- 为 AI 辅助生成内容提供稳定模板
- 保持协作记录清晰、可审查、可追踪
