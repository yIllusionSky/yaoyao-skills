---
name: git-workflow
description: commit、PR、issue、tag、branch 工作流规范技能，生成相关内容时使用
---

# Git Workflow

生成 commit、PR、issue、tag 内容和 branch 命名时使用。

- 不写提交人、协作者、工具来源或 AI 署名。
- 除固定关键词外，使用中文。
- 提交或创建 PR 前，如果本次变更影响项目入口、目录结构、子项目职责、架构边界、功能行为、运行方式、手动测试方式或配置，使用 `project-docs` skill 检查并更新长期文档。

## Branch

- 分支命名使用 `<type>/<short-kebab-summary>`。
- 如果分支包含多类改动，使用主要改动类型；难以归类时使用 `chore`。
- 示例：`docs/update-pr-template`、`fix/remove-codex-prefix`、`feat/add-tag-template`。

## Pull Request

- 新开功能时从 `main` 创建工作分支，并通过 PR 合并回 `main`。
- PR 目标分支默认是 `main`。

## Tag

- 发布 tag 使用 `vX.Y.Z`，例如 `v0.1.0`、`v1.2.3`。
- 创建轻量 tag，不创建 annotated tag。
- 发布 tag 前，使用 `team-changelog` skill 从上一个 semver tag 到当前 `HEAD` 的 commit 区间归纳发布说明，并更新 `CHANGELOG.md` 对应版本区块。
- changelog 版本标题使用 `[X.Y.Z] - YYYY-MM-DD`，版本号不带 `v`。
- tag push 后由 GitHub Actions release workflow 发布 release，并从 changelog 对应版本区块生成 release notes。

需要格式示例或内容参考时，读取对应 reference：

- [commit](./references/commit.md)
- [pull request](./references/pull_request.md)
- [issue](./references/issue.md)
- [tag](./references/tag.md)
