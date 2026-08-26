---
name: changelog
description: 在创建稳定 vX.Y.Z tag 前，根据上一个稳定 semver tag 到当前 HEAD 的最终变化维护 Keep a Changelog 风格的版本区块并准备 release notes。仅用于 tag/release 准备，不在 commit、PR、review 或日常开发阶段维护 changelog。
---

# Changelog

除固定关键词外，使用中文。默认维护仓库根目录 `CHANGELOG.md`。本 skill 只准备 changelog 版本区块和 release notes；提交 changelog、创建和推送 tag 由调用方按 Git 工作流完成。

## 记录原则

- 只记录用户或工程使用者需要了解的最终变化，不记录 commit、PR、review、fixup、amend、返工或测试修复过程。
- 记录新功能、行为变化、breaking change、废弃、移除、已发布能力的修复、安全修复，以及重要的配置、部署或兼容性变化。
- 默认不记录行为不变的重构、格式化、低影响依赖整理、测试补充和内部措辞调整；这些变化影响升级、部署或使用方式时除外。
- 只保留有内容的 `Added`、`Changed`、`Deprecated`、`Removed`、`Fixed`、`Security` 分类，顺序固定。删除空分类、注释和占位列表项。
- 一个发布事项只保留一个条目。同一功能、规则、文件、命令、配置、文档、工作流或工程能力在本次发布前的补充、修正和完善，合并为描述最终状态的一个条目。

判断条目是否应合并存在疑问时，读取 [examples](./references/examples.md)。

## Tag 前流程

1. 确认目标 tag 严格匹配 `vX.Y.Z`；changelog 版本号使用不带 `v` 的 `X.Y.Z`。
2. 从当前 `HEAD` 可达的 tag 中找到版本最高且严格匹配 `vX.Y.Z` 的上一个稳定 semver tag；没有时按首版处理。
3. 读取 commit 正文和 diff，不要把 commit 逐条转换成 changelog：

```bash
git log --reverse --no-merges --format='%H%n%s%n%b%n---' <previous-tag>..HEAD
git diff --stat <previous-tag>..HEAD
git diff --name-status <previous-tag>..HEAD
```

首版使用 `git log ... HEAD` 读取全部 commit；diff 使用空树到 `HEAD` 的范围：

```bash
git hash-object -t tree /dev/null
git diff --stat <empty-tree>..HEAD
git diff --name-status <empty-tree>..HEAD
```

4. 读取现有 `CHANGELOG.md` 的说明文字和历史版本，按发布后的最终状态归纳本次变化。
5. 没有有效条目时停止，不创建空版本。
6. 在顶部说明文字之后、历史版本之前写入 `## [X.Y.Z] - YYYY-MM-DD`；同版本已存在时更新原区块，不重复创建。
7. 清理空分类、占位符和重复条目，并使用该版本区块正文作为 GitHub Release notes。

## 最小格式

```markdown
## [1.2.3] - 2026-07-14

### Added

- 添加示例能力。
```
