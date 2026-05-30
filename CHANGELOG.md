# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 添加根目录 `CHANGELOG.md`。
- 添加 changelog 技能的单文件 `CHANGELOG.md` 维护规则，并明确 `[Unreleased]` 只描述下一次发布后的最终变化，已有同一发布事项应不改或更新原条目，首版 `[Unreleased]` 只能使用 `Added`，发布 tag 时将 `vX.Y.Z` 对应为不带 `v` 且带本地分钟时间的 changelog 版本区块，并通过两个正反示例说明按最终事项维护。
- 添加 `github-actions` 技能，按 assets 和复制脚本维护通用 Rust CI、app / Docker / Tauri tag release workflow，提供约定 `server/` 与 `client/` 分离构建且 Dockerfile 位于各自服务目录的 Docker 项目模板，支持按 Docker 目标架构选择 Rust musl target，并补齐 SvelteKit SSR + TypeScript 客户端模板，同时完善 `git-workflow` 对 changelog 检查、PR 检查、tag 发布、release notes 来源和 reference 示例的规则。
- 添加 `rust-architecture` 技能，规范 Rust CLI、library、后端服务和复杂应用的项目结构、四层架构边界、adapter 拆分、错误处理、crate 级格式化、clippy 检查和测试规则。
- 添加 `project-docs` 技能，规范长期项目文档的创建和维护，包括根 README、子项目 README、根目录架构文档、功能说明和运行维护文档。
- 添加 `project-workflow` 技能，编排 `.workflow/<task-id>/` 本地任务记录、`develop` 集成 worktree、项目 detached worktree、并行 subagent 实现、项目分支逐个 merge、根级配置与长期文档集成、最终 `develop` 总体验收 review 闭环，并通过 references 定义任务格式、主 agent 流程、subagent 流程和 worktree 规则，明确 implementation subagent 无需修改或记录 changelog。

## [<version>] - <YYYY-MM-DD HH:mm>

...
