# Subagent Flow

本参考定义被创建后的执行协议。只按任务说明第一段声明的角色和范围工作。

## Main Agent 下发要求

必须知道自己负责的 `project-worktree`，并且只能修改该 worktree。读取该 worktree 下的 `.skills` 加载所需技能。

## 工作流程

1. 读取任务说明中的 `task.md`。
2. 在自己的 `project-worktree` 中完成任务。
3. 进行review并根据review结果更新log.md和task.md。
4. review 通过时，更新自己 worktree 中的 `.workflow/<task-id>/<project-worktree>/task.md` 状态。
5. review 有问题时，在同一轮内继续修复；无法继续时返回阻塞原因。
