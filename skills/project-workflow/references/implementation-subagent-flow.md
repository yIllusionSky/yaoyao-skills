# Implementation Subagent Flow

本参考只适用于 implementation subagent。implementation subagent 必须先读取 `workspace-layout.md`、`task-format.md` 和 `commit.md`，只能在 main agent 指定的 `project-worktree`、`project-path`、`Allowed Paths`、`workflow/<task-id>/<project-worktree>` 和任务范围内工作。

## Main Agent 下发要求

必须知道自己负责的 `project-worktree`、`project-path`、`Allowed Paths`、`<task-id>`、`workflow/<task-id>/<project-worktree>`、项目 `task.md` 路径和项目 `log.md` 路径。读取该 worktree 下的 `.skills`；文件每行一个 skill 名。无法找到或加载声明的必要 skill 时，停止并返回 main agent。

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

- 项目 `task.md` 中 `Allowed Paths` 列出的路径；其中必须包含 `<project-path>/`
- `.workflow/<task-id>/<project-worktree>/task.md`
- `.workflow/<task-id>/<project-worktree>/log.md`

未列入 `Allowed Paths` 的 package/crate/module 不能自行修改。发现任务需要修改未授权路径时，停止实现并返回 main agent 更新任务授权；不得自行创建额外 project worktree。

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

切换已有分支后确认 `<task-id>` 是其祖先；不是时停止并返回 main agent，不在错误基线上继续实现：

```bash
git merge-base --is-ancestor <task-id> HEAD
```

6. 在自己的 `project-worktree` 中，只修改 `Allowed Paths` 和对应 workflow 记录；实现完成后，如本次变更影响当前子项目入口、职责、功能行为、运行方式、手动测试方式或配置，使用 `project-docs` 技能更新当前子项目长期文档；不得在 workspace 根创建或修改 `apps/`、`packages/`、`crates/` 等 `<project-path>` 父目录。
7. 运行必要自测，根据结果更新 `.workflow/<task-id>/<project-worktree>/log.md` 和 `task.md`。
8. 提交 commit。
9. 若自测失败，根据反馈回到第 6 步继续修改。
10. 返回执行结果和测试结果。
