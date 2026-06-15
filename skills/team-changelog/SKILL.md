---
name: team-changelog
description: 团队 tag-only changelog 和 release notes 维护规则。用于发布前、创建 tag 前、整理版本说明、维护 `CHANGELOG.md` 版本区块、从上一个 semver tag 到当前 HEAD 的 commit 区间归纳发布内容。
---

# Team Changelog

## Rule

- 除固定关键词外，使用中文。
- 只在发布 tag 前维护仓库根目录 `CHANGELOG.md`。
- tag 使用 `vX.Y.Z`；changelog 标题使用 `## [X.Y.Z] - YYYY-MM-DD`。
- release notes 来源于 changelog 对应版本区块。

## Tag 前流程

1. 确认 tag 名符合 `vX.Y.Z`，changelog 版本号使用不带 `v` 的 `X.Y.Z`。
2. 找到上一个 semver tag：

```bash
git describe --tags --match 'v[0-9]*.[0-9]*.[0-9]*' --abbrev=0
```

没有上一个 tag 时，按首版发布处理。

3. 读取 commit 区间：

```bash
git log --reverse --no-merges --format='%h %s' <previous-tag>..HEAD
```

首版发布时使用：

```bash
git log --reverse --no-merges --format='%h %s'
```

4. 按发布后的最终变化归纳，不描述开发过程。
5. 在 `CHANGELOG.md` 顶部说明文字之后、历史版本之前插入版本区块；同版本已存在时更新原区块。
6. 提交 changelog 变更后再创建轻量 tag。

## Template

```markdown
## [<version>] - <YYYY-MM-DD>

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

## [<previous-version>] - <YYYY-MM-DD>

...
```
