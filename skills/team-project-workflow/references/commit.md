# Commit

生成 `team-project-workflow` 中的 commit 内容时使用。

- 不写提交人、协作者、工具来源或 AI 署名。
- commit subject、body 和 footer 必须使用英文；不要使用中文描述提交内容。

## Format

```text
<type>[optional scope]: <description>

<body when needed>

<footer when needed>
```

## Reference

- `type`: `feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`
- `scope`: 可选；变更限制在清晰范围内时使用。
- `description`: 简短描述。
- `body`: 默认需要；说明原因、上下文、影响或风险。仅当 subject 已完整表达简单变更时可省略。
- `footer`: 仅在 breaking change、issue reference 或迁移说明需要时使用。

## Example

```text
fix(auth): refresh login session state

Refreshing the token did not update the local session, so page reloads could still be treated as unauthenticated.
The refresh path now writes the session state after success to keep authentication state aligned with API state.
```
