# Implementation Subagent Flow

本参考只适用于 implementation subagent。implementation subagent 必须先读取 `workspace-layout.md` 和 `task-format.md`，只能在 main agent 指定的 `project-worktree`、`project-path`、`workflow/<task-id>/<project-worktree>` 和任务范围内工作。

## Main Agent 下发要求

必须知道自己负责的 `project-worktree`、`project-path`、`<task-id>`、`workflow/<task-id>/<project-worktree>`、项目 `task.md` 路径和项目 `log.md` 路径。读取该 worktree 下的 `.skills` 加载所需技能。

## 工作目录

所有文件读写、shell 命令、git 命令都必须在 `project-worktree` 根目录执行。禁止在 workspace 根、`develop/`、`main/` 或其他 `<project-worktree>/` 内执行实现、测试或提交。

执行任何修改前，必须确认当前目录和 git root 都是 `project-worktree`：

```bash
pwd
git rev-parse --show-toplevel
```

如果当前目录或 git root 不是 `project-worktree`，先切换到 `project-worktree`；无法切换时停止并返回 main agent。

以下路径均相对 `project-worktree` 根目录。`<project-path>` 是 worktree 内相对路径，不是 workspace 根路径。

只能修改：

- `<project-path>/`
- `.workflow/<task-id>/<project-worktree>/task.md`
- `.workflow/<task-id>/<project-worktree>/log.md`

如使用 `project-docs` 技能，只需更新 `<project-path>/README.md`。

无需修改或记录 changelog。

## 工作流程

1. 确认工作目录符合“工作目录”要求。
2. 读取 main agent 下发的项目 `task.md`。
3. 确认当前 worktree 状态：

```bash
git status --short
```

如果存在输出，先分析改动来源：之前忘记提交、任务未写完、或其他原因。根据判断继续完成、提交或返回需要 main agent 处理的信息；不得覆盖或丢弃改动。

4. worktree 干净时，切到 detached 的 `<task-id>` 集成基线：

```bash
git switch --detach <task-id>
```

5. 创建或切到任务分支：

```bash
git switch -c workflow/<task-id>/<project-worktree>
```

如果分支已存在，切到该分支继续：

```bash
git switch workflow/<task-id>/<project-worktree>
```

6. 在自己的 `project-worktree` 中，只修改 `<project-path>` 和对应 workflow 记录；不得在 workspace 根创建或修改 `apps/`、`packages/`、`crates/` 等 `<project-path>` 父目录。
7. 运行必要自测，先根据结果更新 `.workflow/<task-id>/<project-worktree>/log.md` 和 `task.md`。
8. 提交 commit。
9. 若自测失败，根据反馈回到第 6 步继续修改。
10. 返回执行结果和测试结果。
