---
name: git-workflow
description: commit、PR、issue、tag、branch 工作流规范技能，生成相关内容时使用
---

# Git Workflow

生成 commit、PR、issue、tag 内容和 branch 命名时使用。

- 不写提交人、协作者、工具来源或 AI 署名。
- 除固定关键词外，使用中文。
- 提交、创建 PR 或发布 tag 前，检查本次用户或工程上有意义的变更是否已记录到 changelog，使用 `changelog` skill；未记录则补充记录。

## Branch

- 默认分支为 `main`，不直接在 `main` 上提交。
- 提交前从 `main` 创建工作分支，并按用户要求通过 PR 或 squash merge 合并回 `main`。
- 分支命名使用 `<type>/<short-kebab-summary>`。
- 如果分支包含多类改动，使用主要改动类型；难以归类时使用 `chore`。
- 示例：`docs/update-pr-template`、`fix/remove-codex-prefix`、`feat/add-tag-template`。

## Pull Request

- 新开功能时从 `main` 创建工作分支，并通过 PR 合并回 `main`。
- PR 目标分支默认是 `main`。
- PR 合并到 `main` 时只做 CI 检查，不发布、不打包 release。
- 提交或合并 PR 前，确认 CI workflow 已配置并通过。

## Tag

- 发布 tag 使用 `vX.Y.Z`，例如 `v0.1.0`、`v1.2.3`。
- 创建轻量 tag，不创建 annotated tag。
- 发布 tag 前，先按 changelog 规则将 `[Unreleased]` 转为 `[X.Y.Z] - <YYYY-MM-DD>`；changelog 版本号不带 `v`。
- tag push 后由 GitHub Actions release workflow 发布 release，并从 changelog 对应版本区块生成 release notes。

需要格式示例或内容参考时，读取对应 reference：

- [commit](./references/commit.md)
- [pull request](./references/pull_request.md)
- [issue](./references/issue.md)
- [tag](./references/tag.md)
