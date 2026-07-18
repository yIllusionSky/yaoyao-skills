# Pull Request

优先使用仓库已有 PR 模板。没有模板时使用以下最小结构，删除不适用的空章节。

```markdown
## Summary

- 说明变更解决的问题和最终效果。

## Changes

- 列出关键实现或行为变化。

## Tests

- `实际运行的命令`：结果。

## Related

- Closes #123
```

标题使用与 commit subject 相同的 `<type>[optional scope]: <description>` 结构。只有确实关联 issue 时保留 `Related`。
