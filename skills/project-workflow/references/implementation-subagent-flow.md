# Implementation Subagent Flow

## Main Agent 下发要求

确认 `project-worktree`、`project-path`、`Allowed Paths`、`<task-id>`、`Base Commit` 及项目任务和日志路径。读取 worktree 下 `.skills` 中声明的必要 skill；无法加载时返回 main agent。

## 工作目录

项目文件操作和命令以 `project-worktree` 根目录为工作目录；必要的技能和依赖资料可按其实际路径读取。禁止在其他 worktree 或编排目录执行实现、测试或提交。

执行任何修改前，必须确认当前目录和 git root 都是 `project-worktree`：

```bash
pwd
git rev-parse --show-toplevel
```

如果当前目录或 git root 不是 `project-worktree`，先切换到 `project-worktree`；无法切换时停止并返回 main agent。

可修改的项目路径：

- 项目 `task.md` 中 `Allowed Paths` 列出的路径；其中必须包含 `<project-path>`
- `.workflow/<task-id>/<project-worktree>/task.md`
- `.workflow/<task-id>/<project-worktree>/log.md`

额外路径交由 main agent 协调，不自行创建 worktree。依赖安装和根锁文件遵守主 skill 的执行范围。

## 工作流程

1. 确认工作目录符合“工作目录”要求。
2. 读取 main agent 下发的项目 `task.md`，确认每个 `Allowed Paths` 都符合 `task-format.md` 的规范化相对路径要求；存在无效路径时停止并返回 main agent。
3. 确认当前 worktree 状态：

```bash
git status --short
```

本任务安装自动生成的根锁文件修改可保留；其他修改先确认来源并保留已有进度。切换或同步被锁文件阻挡时，仅恢复已确认由本任务自动生成的修改，不覆盖来源不明的内容。

4. 首次执行时确认当前 HEAD 包含下发的 `Base Commit`，从 main agent 准备的基线创建项目分支：

```bash
git switch -c workflow/<task-id>/<project-worktree>
```

恢复任务时保留原有进度，必要时切回已有项目分支；不先切到移动中的任务分支：

```bash
git switch workflow/<task-id>/<project-worktree>
```

5. 确认记录的 `Base Commit` 是当前分支祖先：

```bash
git merge-base --is-ancestor <base-commit> HEAD
```

检查通过即可继续未集成的任务，任务分支前进本身不构成异常。检查失败，或已集成后收到修复任务时，交由 main agent 按 main flow 同步基线再继续。

6. 实现本任务，使用 `project-docs` 按本次 diff 更新受影响的子项目文档。
7. 运行必要自测，失败时继续修复；把本轮结果写入项目日志，更新任务状态。
8. 检查实际提交范围，排除根锁文件后提交，返回 commit SHA、执行结果和测试结果。
