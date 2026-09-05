# Review Subagent Flow

只读审查 main agent 指定的 `develop/` 候选版本，不修改代码或记录，不提交 commit。

## Main Agent 下发要求

确认 `develop/`、`<task-id>`、`Base Commit`、`Reviewed Commit` 及根任务和日志路径。

审查范围包括：

- 已 merge 的项目改动。
- 根配置、workspace 配置和跨项目集成。
- 根 README、架构文档、项目 README、功能或运维文档。
- `.workflow/<task-id>/` 下的根记录和项目记录。
- 结合项目实现提交和派发记录核对 `Allowed Paths`，不把同步基线带入的其他项目改动算作该子代理实现。
- 已记录的测试结果和遗漏的必要测试。
- workspace 是否符合 workspace layout，包括允许的编排控制文件。

## 工作流程

1. 确认当前分支为 `<task-id>`，HEAD 等于下发的 `Reviewed Commit`，工作区干净，且 `Base Commit` 是候选版本的祖先：

```bash
git -C develop branch --show-current
git -C develop rev-parse HEAD
git -C develop status --short
git -C develop merge-base --is-ancestor <base-commit> <reviewed-commit>
```

不符合时返回 main agent 整理候选版本，不对不完整或变化中的状态给出通过结论。

2. 审查两个固定提交间的完整变化，并读取候选版本中的任务记录和必要上下文：

```bash
git -C develop diff <base-commit> <reviewed-commit>
```

3. 返回前再次确认 HEAD 和工作区未变化。结果带上两个 SHA，按严重程度输出 findings，每条包含可定位位置、风险和修复建议。
4. 未发现阻断问题时明确说明，并列出实际存在的剩余风险或未覆盖测试。
