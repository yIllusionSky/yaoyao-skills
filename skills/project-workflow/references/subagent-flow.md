# Subagent Flow

本参考只适用于 implementation subagent。subagent 只能在 main agent 指定的 `project-worktree`、`workflow/<task-id>/<project-worktree>` 和任务范围内工作。

## Main Agent 下发要求

必须知道自己负责的 `project-worktree` 和 `workflow/<task-id>/<project-worktree>`，并且只能修改该 worktree。读取该 worktree 下的 `.skills` 加载所需技能。

## 工作流程

1. 根据 `workflow/<task-id>/<project-worktree>` 读取 `.workflow/<task-id>/<project-worktree>/task.md`。
2. 确认当前 worktree 状态：

```bash
git status --short
```

如果存在输出，先分析改动来源：之前忘记提交、任务未写完、或其他原因。根据判断继续完成、提交或返回需要 main agent 处理的信息；不得覆盖或丢弃改动。

3. worktree 干净时，切到 detached 的 `develop`：

```bash
git switch --detach develop
```

4. 创建或切到任务分支：

```bash
git switch -c workflow/<task-id>/<project-worktree>
```

如果分支已存在，切到该分支继续：

```bash
git switch workflow/<task-id>/<project-worktree>
```

5. 在自己的 `project-worktree` 中完成任务。
6. 运行必要自测，先根据结果更新 `.workflow/<task-id>/<project-worktree>/log.md` 和 `task.md`。
7. `log.md` 和 `task.md` 更新完成后，再提交 commit；无论自测通过或失败都要提交，commit message 写具体变更语义。
8. 若自测失败，根据反馈回到第 5 步继续修改。
9. 返回执行结果、commit hash 和测试结果。
