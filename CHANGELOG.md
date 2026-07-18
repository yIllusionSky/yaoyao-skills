# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 添加根目录 `CHANGELOG.md`。
- 添加独立 `changelog` 技能，持续维护只描述最终变化的 `[Unreleased]`，在稳定 semver tag 前结合 commit 正文和 diff 审计条目，使用不带时间的 ISO 日期发布版本区块，并通过按需加载的示例说明同一发布事项的归并规则。
- 添加 `github-actions` 技能，通过校验后一次性复制的脚本维护 Rust CI、app、Docker 和 Tauri tag release workflow；Docker assets 作为已有 server/client 项目的部署叠加层，支持 server-only 与 fullstack，固定 Action SHA，并完善 `git-workflow` 的中文 commit、PR、issue、tag 和两种 changelog 模式选择规则。
- 添加 `rust-architecture` 技能，规范 Rust CLI、library、后端服务和复杂应用的四层边界、模块入口、按复杂度选择的错误处理、library public API、条件 REST 错误契约、本地 crate 级检查、workspace CI 和测试规则。
- 添加 `project-docs` 技能，规范根 README、子项目 README、架构、功能、运维和按 CLI、HTTP、browser、desktop、library 入口区分的手动测试文档，并要求更新后核对链接、命令、路径和配置。
- 添加互斥安装的 `project-workflow` 和 `team-project-workflow`，通过显式项目白名单、任务记录、detached project worktree、受限 `Allowed Paths`、按可用 slot 分批执行、项目分支集成和 review subagent 完成多项目闭环；非 team 版始终从 `main` 派生并交付任务分支，team 版验收后使用 merge commit 合并回真实 `develop`。
