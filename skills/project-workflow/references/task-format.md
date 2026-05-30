# Task Format

## 目录

```text
项目/
├── develop/
│   └── .workflow/
│       └── <task-id>/
│           ├── task.md
│           ├── log.md
│           └── <project-worktree>/
│               ├── task.md
│               └── log.md
├── main/
├── crates-auth/
│   └── .skills
├── packages-ui/
│   └── .skills
└── apps-web/
    └── .skills
```

## 命名

- `<task-id>`：任务包标识，小写字母、数字和 `-`；已存在时追加 `-2`、`-3`。
- `<project-worktree>`：项目相对路径去掉结尾 `/`，把 `/` 替换为 `-`；例如 `crates/auth` -> `crates-auth`

## Task 模板

```markdown
# <标题>

Status: <in-progress|blocked|completed>

## Summary

...

## Implementation Plan

-

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

- 新日志写在 `Log` 下最上方。
- 可按需增加 `Notes`。
- `blocked` 只在用户明确表示暂不实现或不需要该功能时使用，不由 agent 因执行失败自行设置。
