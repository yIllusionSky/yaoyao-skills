# yaoyao-skills

一组用于统一项目协作规范的技能包。

该仓库提供简洁的中文项目规范，适合在 Codex、Copilot 或其他支持技能 / 提示词的工作流中复用，减少多人协作时格式和记录风格不一致的问题。

> [!NOTE]
> 本仓库内技能要求除固定关键词外尽量使用中文，不写提交人、协作者、工具来源或 AI 署名。

## Skills

- `git-workflow`: 规范 branch、commit、PR、issue 和 tag。
- `github-actions`: 规范 GitHub Actions CI、app、Tauri 2 和 Docker 的 tag release workflow，并为 Rust 项目、TypeScript + Rust monorepo、独立 server 与可选 SvelteKit adapter-node client 提供可复制 assets 和复制脚本。
- `changelog`: 只在 tag/release 前根据稳定 semver tag 间的最终变化整理 `CHANGELOG.md` 版本区块和 release notes。
- `rust-architecture`: 规范 Rust CLI、library、后端服务、Cargo workspace 与按业务组织的 TypeScript + Rust monorepo，包括模块与 crate 边界、四层依赖、跨语言契约、增长控制、错误和测试结构。
- `project-docs`: 规范长期项目文档，包括根 README、子项目 README、架构文档、功能说明、手动测试和运行维护文档。
- `project-workflow`: 以本地 `main` 为基线，编排 `.workflow` 任务记录、`develop/` 集成 worktree、implementation subagent、review subagent，并在验收后将任务分支合并回 `main`。

## 项目目标

- 统一项目协作内容的书写格式
- 降低团队在提交描述上的沟通成本
- 为 AI 辅助生成内容提供稳定模板
- 保持协作记录清晰、可审查、可追踪
