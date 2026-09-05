# Task Format

## 命名

- `<task-id>`：任务包标识，小写字母、数字和 `-`；已存在时追加 `-2`、`-3`。
- `<project-path>`：monorepo 内真实项目路径，例如 `apps/backend`。
- `<project-worktree>`：默认由 `<project-path>` 去掉结尾 `/`，把 `/` 替换为 `-` 得到；例如 `apps/backend` -> `apps-backend`。按 `.workflow/.projects` 顺序分配；如果名称已被前面的项目占用，依次追加 `-2`、`-3` 直到唯一。
- `Allowed Paths`：仅用于 `.workflow/<task-id>/<project-worktree>/task.md`；每一项必须是规范化的 worktree 相对路径，不得是绝对路径，不得包含值为 `.` 或 `..` 的路径组件，也不得逃出 worktree。`.github`、`Cargo.toml` 等名称中的 `.` 不受限制。必须包含 `<project-path>`；额外可写路径必须由 main agent 显式列出，未列出的路径不得修改。
- `Base Commit`：项目任务记录中表示最近一次派发或同步所依据的完整 SHA，指向填写字段前已存在的提交；审查日志中表示本轮 `main` 基线。
- `Reviewed Commit`：审查日志中表示本轮候选版本的完整 SHA。

## Task 模板

```markdown
# <标题>

Status: <in-progress|blocked|completed|cancelled>
Base Commit: <项目派发或同步基线；根 task 省略>

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

Base Commit: <main 基线 SHA>
Reviewed Commit: <候选 SHA>
Status: <changes requested|passed>

-
```

## 规则

- `task.md` 维护当前目标、范围、基线和状态；`log.md` 只追加本轮执行、测试、集成或 review 的增量结果。
- 新日志写在 `Log` 下最上方。
- 空章节省略，只有发生审查时填写 `Review`，可按需增加 `Notes`。
- `Key Changes` 写任务的关键改动范围，不重复日志历史或通用步骤。
- 已有任务恢复时按可验证的提交和派发记录补齐缺失基线，不批量改写历史；无法确认时交由 main agent 调查。
- `completed` 表示对应任务已完成并通过对应验收。
- `blocked` 表示存在依赖、权限、外部状态或必要输入等真实阻塞，当前无法继续推进；把原因和解除条件写入日志。
- `cancelled` 表示用户取消任务或将其移出范围。
- 普通测试失败、review finding 或可继续修复的实现错误保持 `in-progress`。
