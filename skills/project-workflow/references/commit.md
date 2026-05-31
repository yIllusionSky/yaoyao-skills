# Commit

生成 `project-workflow` 中的 commit 内容时使用。

- 不写提交人、协作者、工具来源或 AI 署名。
- 除固定关键词外，使用中文。

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
fix(auth): 修复登录状态刷新失败

刷新 token 时未同步更新本地会话，导致页面刷新后仍被识别为未登录。
现在在刷新成功后统一写入会话状态，避免认证状态和接口状态不一致。
```
