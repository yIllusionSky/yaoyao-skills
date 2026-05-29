# Task Format

## 目录

```text
项目/
├── develop/
│   └── .workflow/
│       └── <task-id>/
│           ├── task.md
│           ├── log.md
│           └── <project-dir>/
│               ├── task.md
│               └── log.md
├── main/
├── crates-auth/
│   ├── .workflow/
│   │   └── <task-id>/
│   │       └── crates-auth/
│   │           ├── task.md
│   │           └── log.md
│   └── .skills
├── packages-ui/
│   ├── .workflow/
│   │   └── <task-id>/
│   │       └── packages-ui/
│   │           ├── task.md
│   │           └── log.md
│   └── .skills
└── apps-web/
    ├── .workflow/
    │   └── <task-id>/
    │       └── apps-web/
    │           ├── task.md
    │           └── log.md
    └── .skills
```

## 命名

- `<task-id>`：小写字母、数字和 `-`；已存在时追加 `-2`、`-3`。
- `<project-dir>`：项目相对路径去掉结尾 `/`，把 `/` 替换为 `-`；例如 `crates/auth` -> `crates-auth`

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
# Work Log

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

- 新日志写在 `Work Log` 下最上方。
- 项目 subagent 写自己的项目 `task.md` 和 `log.md`。
- 项目 subagent 在项目日志中写 `Changed`、`Tests` 和自 review 的 `Review`。
- 总体验收 review subagent 不写文件，由 main agent 根据 review 结果更新根 `log.md` 和需要返工的项目 `task.md`。
- 可按需增加 `Notes`。
