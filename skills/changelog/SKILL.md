---
name: changelog
description: 维护 Keep a Changelog 风格的 CHANGELOG.md；在开发和 PR 集成期间维护 [Unreleased]，在创建 vX.Y.Z tag 前审计变更、发布版本区块并准备 release notes。用于持续维护 changelog 的项目，不用于每个 commit、fixup 或 review 修复。
---

# Changelog

除固定关键词外，使用中文。默认维护仓库根目录 `CHANGELOG.md`。

## 维护原则

- 只记录用户或工程使用者需要了解的最终变化，不记录 commit、PR、review、fixup、amend、返工或测试修复过程。
- 记录新功能、行为变化、breaking change、废弃、移除、已发布能力的修复、安全修复，以及重要的配置、部署或兼容性变化。
- 默认不记录行为不变的重构、格式化、低影响依赖整理、测试补充和内部措辞调整；这些变化影响升级、部署或使用方式时除外。
- 只保留有内容的 `Added`、`Changed`、`Deprecated`、`Removed`、`Fixed`、`Security` 分类，顺序固定。删除空分类、注释和占位列表项。
- 一个发布事项只保留一个条目。同一功能、规则、文件、命令、配置、文档、工作流或工程能力在发布前的补充、修正和完善，更新已有条目，不新增过程条目。

## 维护 `[Unreleased]`

按以下顺序处理：

1. 读取当前 `[Unreleased]` 的全部条目和历史版本。
2. 判断本次变化是否属于已有发布事项。
3. 已有条目准确描述最终状态时不修改；不准确时更新原条目。
4. 只有独立且值得在下一次发布说明中出现的最终变化，才新增条目。
5. 清理空分类、占位符和重复条目。

没有任何真实发布版本时，将 `[Unreleased]` 视为首版内容。首版默认只使用 `Added`；发布前的修正合并进对应 `Added` 条目，不单独记录为 `Changed`、`Removed` 或 `Fixed`。

判断条目是否应合并存在疑问时，读取 [examples](./references/examples.md)。

## 发布版本

发布前先确认目标 tag 严格匹配 `vX.Y.Z`。找到当前 `HEAD` 可达的上一个稳定 semver tag；没有时按首版处理。

使用 commit 正文和 diff 审计 `[Unreleased]`，不要把 commit 逐条转换成 changelog：

```bash
git log --reverse --no-merges --format='%H%n%s%n%b%n---' <previous-tag>..HEAD
git diff --stat <previous-tag>..HEAD
git diff --name-status <previous-tag>..HEAD
```

首版省略 `<previous-tag>..`。审计后：

1. 补充遗漏的重要变化，修正与最终实现不一致的描述。
2. 没有有效条目时停止，不创建空版本。
3. 将当前 `[Unreleased]` 内容发布为 `## [X.Y.Z] - YYYY-MM-DD`，版本号不带 `v`，日期不带时间。
4. 在顶部重新创建空的 `## [Unreleased]`。
5. 使用新版本区块正文作为 GitHub Release notes。

## 最小格式

```markdown
## [Unreleased]

## [1.2.3] - 2026-07-14

### Added

- 添加示例能力。
```
