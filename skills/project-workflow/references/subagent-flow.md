# Subagent Flow

本参考只适用于 implementation subagent。subagent 只能在 main agent 指定的 `project-worktree`、`<task-branch>` 和任务范围内工作。

## Main Agent 下发要求

必须知道自己负责的 `project-worktree`、`<task-branch>`，并且只能修改该 worktree。读取该 worktree 下的 `.skills` 加载所需技能。

## 工作流程

1. 读取任务说明中的 `task.md`。
2. 确认当前 worktree 状态；如果处于 detached HEAD，创建或切到任务分支：

```bash
git switch -c <task-branch>
```

如果分支已存在，切到该分支继续：

```bash
git switch <task-branch>
```

3. 在自己的 `project-worktree` 中完成任务。
4. 对当前修改进行review，并根据结果更新 `.workflow/<task-id>/<project-worktree>/log.md` 和 `task.md`。
5. commit提交
6. 若review失败，从第三步重新进行修改。review成功结束任务
