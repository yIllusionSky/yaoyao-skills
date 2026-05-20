# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 添加根目录 `CHANGELOG.md`。
- 添加 changelog 技能的单文件 `CHANGELOG.md` 维护规则，并明确 `[Unreleased]` 只描述下一次发布后的最终变化，已有同一发布事项应更新原条目，发布 tag 时将 `vX.Y.Z` 对应为不带 `v` 的 changelog 版本区块，并通过两个正反示例说明按最终事项维护。
- 添加 `github-actions` 技能，按模板维护通用 Rust CI、app / Docker / Tauri tag release workflow，提供面向根目录 Rust/Bun workspace 的 Docker 项目模板和 Rust 构建 profile，并完善 `git-workflow` 对分支创建失败处理、PR 检查、tag 发布和 release notes 来源的规则。

## [<version>] - <YYYY-MM-DD>

...
