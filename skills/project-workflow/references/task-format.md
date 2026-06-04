# Task Format

## 命名

- `<task-id>`：任务包标识，小写字母、数字和 `-`；已存在时追加 `-2`、`-3`。
- `<project-path>`：monorepo 内真实项目路径，例如 `apps/backend`。
- `<project-worktree>`：由 `<project-path>` 去掉结尾 `/`，把 `/` 替换为 `-` 得到；例如 `apps/backend` -> `apps-backend`
- `Allowed Paths`：仅用于 `.workflow/<task-id>/<project-worktree>/task.md`；必须包含 `<project-path>`，额外可写路径必须由 main agent 显式列出，未列出的路径不得修改。

## Task 模板

```markdown
# <标题>

Status: <in-progress|blocked|completed>

## Summary

...

## Key Changes

-

## Allowed Paths

仅用于 `.workflow/<task-id>/<project-worktree>/task.md`；根 `task.md` 省略。

- `<project-path>`

## Acceptance Criteria

- [ ]

## Test Plan

-

## Assumptions

-
```

## Log 模板

```markdown
# Log

## <标题> YYYY-MM-DD HH:mm

### Changed

-

### Tests

-

### Review

Status: <pending|changes requested|passed>

-

## <标题> YYYY-MM-DD HH:mm

...
```

## 规则

- 日志用于记录执行、测试、集成或 review 后的结果。
- 新日志写在 `Log` 下最上方。
- 可按需增加 `Notes`。
- `Key Changes` 写本任务需要完成或已经完成的关键改动，不写通用执行步骤。
- `completed` 表示对应任务已完成。
- `blocked` 只在用户明确表示暂不实现或不需要该功能时使用，不由 agent 因执行失败自行设置。
