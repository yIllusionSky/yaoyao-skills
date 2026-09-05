---
name: git-workflow
description: 生成或审查 branch、commit、pull request、issue 和 tag 内容，并在提交、PR 与发布前执行对应检查。用于 Git 协作内容、分支命名、GitHub issue/PR 和 semver tag 工作流。
---

# Git Workflow

- 不写提交人、协作者、工具来源或 AI 署名。
- 除固定关键词、命令和代码符号外，使用中文。
- 先读取仓库现有模板、贡献规范和目标分支，再生成或更新内容；不要用通用模板覆盖仓库规则。
- 只生成或审查 Git 内容时不扩展为实现任务；提交或创建 PR 前，按实际 diff 使用 `project-docs` 检查受影响的长期文档，不补齐无关历史缺项。

## Branch

- 使用 `<type>/<short-kebab-summary>`。
- 从仓库约定的基线分支创建；没有其他约定时使用 `main`。
- 多类改动使用主要类型，难以归类时使用 `chore`。
- 示例：`docs/update-pr-template`、`fix/remove-invalid-prefix`、`feat/add-tag-template`。

## Commit

需要生成或审查 commit 时读取 [commit](./references/commit.md)。

## Pull Request

- 默认目标分支为仓库约定的基线；没有其他约定时使用 `main`。
- 创建 PR 前检查工作区状态、实际 diff、测试结果和需要同步的长期文档。
- commit 和 PR 阶段不调用 `changelog`，不修改 `CHANGELOG.md`。
- 需要格式时读取 [pull request](./references/pull_request.md)。

## Issue

- 创建或更新 issue 前读取仓库上下文和现有 issue；缺少关键信息时明确列为待确认项，不自行编造。
- 只有确认仓库中存在对应 label 后才使用 label。
- 更新 issue 时保留未要求修改的字段。
- 需要格式时读取 [issue](./references/issue.md)。

## Tag

- 只创建严格匹配 `vX.Y.Z` 的轻量 tag，不创建 annotated tag。
- 项目安装 `changelog` 时，先使用它从上一个稳定 semver tag 到当前 `HEAD` 归纳版本区块和 release notes。
- 未安装 `changelog` 时，不自行修改 changelog；停止并报告缺少发布说明来源。
- 确认目标版本区块为 `## [X.Y.Z] - YYYY-MM-DD`，提交 changelog 后创建 tag，例如 `git tag v1.2.3`。
- tag push 后由 release workflow 从对应版本区块生成 release notes。
