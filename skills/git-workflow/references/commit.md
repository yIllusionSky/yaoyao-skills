# Commit

使用以下格式：

```text
<type>[optional scope]: <description>

<body when needed>

<footer when needed>
```

- `type`：`feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`。
- `scope`：变更限制在清晰范围内时使用。
- `description`：用中文简短描述最终变化。
- `body`：默认说明原因、上下文、影响或风险；subject 已完整说明简单变更时省略。
- `footer`：只在 breaking change、issue reference 或迁移说明需要时使用。

```text
fix(auth): 修复登录状态刷新失败

刷新 token 时未同步更新本地会话，导致页面刷新后仍被识别为未登录。
现在在刷新成功后统一写入会话状态，避免认证状态和接口状态不一致。
```
