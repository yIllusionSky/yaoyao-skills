---
name: changelog
description: 用于记录项目开发和发布过程中的有意义变更，并维护 changelog、版本记录和发布说明。
---

# Changelog

## Rule

- 除固定关键词外，使用中文。
- 默认维护仓库根目录 `CHANGELOG.md`。
- 有意义的用户或工程变更，应体现在 `CHANGELOG.md` 的 `[Unreleased]` 区块；如果属于已有发布事项，更新原条目；如果是独立发布事项，新增条目。没有该区块时先创建。
- 发布 tag 时，将当前 `[Unreleased]` 标题改为 `[<version>] - <YYYY-MM-DD>`。
- 维护 `[Unreleased]` 时，遵循下面的记录原则。

## [Unreleased] 记录原则

`[Unreleased]` 只描述下一次发布后的最终变化，不记录开发过程。

写入前，先检查当前 `[Unreleased]` 是否已有同一发布事项。

如果已有，就改那条记录，让它描述最终状态；不要新增条目或扩展结构来记录这次修改。

“同一发布事项” 按发布说明中的含义判断，不按本次开发动作判断；同一功能、规则、文件、命令、配置、文档、工作流或工程能力的补充、调整、修正、替换、完善，都属于同一事项。

只有无法归入已有事项，并且发布时需要单独说明，才新增条目。

## 示例

错误：

```markdown
### Added

- 添加导出报表功能。

### Fixed

- 修复导出报表时筛选条件丢失的问题。
```

正确：

```markdown
### Added

- 添加导出报表功能，并支持保留当前筛选条件。
```

## Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

<!-- 新添加的功能。 -->

-

### Changed

<!-- 对现有功能的变更。 -->

-

### Deprecated

<!-- 已经不建议使用、未来会移除的功能。 -->

-

### Removed

<!-- 已经移除的功能。 -->

-

### Fixed

<!-- 对 bug 的修复。 -->

-

### Security

<!-- 对安全性的改进。 -->

-

## [<version>] - <YYYY-MM-DD>

...
```
