# Review Subagent Flow

本参考只适用于 review subagent。review subagent 只审查 main agent 指定的 `develop/` worktree 当前 `<task-id>` 分支状态，不直接修改文件。

## Main Agent 下发要求

必须知道审查对象是 `develop/`、`<task-id>`、根 `task.md` 路径和根 `log.md` 路径。读取 `workspace-layout`、`task-format` 和 `commit`，并按 code review 方式输出结果。

审查范围包括：

- 已 merge 的项目改动。
- 根配置、workspace 配置和跨项目集成。
- 根 README、架构文档、项目 README、功能或运维文档。
- `.workflow/<task-id>/` 下的根记录和项目记录。
- 已记录的测试结果和遗漏的必要测试。
- workspace 根目录是否只包含 `main/`、`develop/` 和 `<project-worktree>/`，是否错误出现 `apps/`、`packages/`、`crates/` 等 monorepo 项目路径父目录。

## 工作流程

1. 确认 `develop/` 当前分支是 `<task-id>`：

```bash
git -C develop branch --show-current
```

2. 检查 `develop/` 当前状态：

```bash
git -C develop status --short
```

3. 审查当前 `<task-id>` 分支相对 `main` 的变更：

```bash
git -C develop diff main...HEAD
```

4. 按严重程度输出 findings。每条 finding 必须包含文件路径、行号或可定位位置、风险说明和建议修复方式。
5. 如果没有发现阻断问题，明确说明未发现阻断问题，并列出剩余风险或未覆盖测试。
6. 不提交 commit，不修改代码，不更新记录。
