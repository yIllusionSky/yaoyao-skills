# Main Agent Flow

本参考定义 main agent 的任务编排协议。main agent 负责任务记录、项目拆分、worktree 编排、subagent 启动、主集成和总体验收。

## 工作区初始化

1. main agent 的工作范围是 `develop/`。
2. 项目主目录不是 git worktree；`.git` 位于 `main/`、`develop/` 和项目 worktree 内。
3. 如果 `develop/` 不存在，从 `main/` 创建：

```bash
git -C main worktree add ../develop develop
```

4. 如果 `main/` 不存在或不可用，停止并报告缺少 main worktree。
5. 后续主集成、根配置、跨项目检查都在 `develop` worktree 中执行。

## 项目初始化

1. 项目 worktree 使用项目目录名作为固定路径名。
2. 项目目录名由项目相对路径归一化得到：去掉结尾 `/`，把 `/` 替换为 `-`。

```text
crates/auth -> crates-auth/
```

3. 同一个项目在不同任务中复用同一个项目级 worktree 目录；项目删除时删除对应 worktree。
4. 项目 worktree 不存在时，从 `develop` 分支创建：

```bash
git -C develop worktree add --detach ../<project-worktree> develop
```

5. 每轮项目 subagent 启动前，将项目 worktree 对齐到 `develop` 分支：

```bash
git -C <project-worktree> reset --hard develop
```

6. 在 `<project-worktree>/.skills` 写入该项目需要使用的技能名，必须包含 `project-workflow`，每行一个；`.gitignore` 忽略 `.skills`。


## 工作流程

1.**完成计划**
  1. 创建task-id
  2. 在 `develop/.workflow/<task-id>/` 创建或更新总 `task.md`。
  3. 分析是否需要额外创建独立项目，例如前端、后端、`crates/<name>`、`packages/<name>`等等，若需要，参考项目初始化。
  4. `.workflow/<task-id>/<project-worktree>/` 创建或更新对应项目的 `task.md`。

2.**执行任务**
  1. 给每个子task.md创建对应的subagent去完成，subagent需要知道自己所需修改的项目
  2. 等待每个subagent完成，当<project-worktree>的task.md status为completed时，main agent才能视为该项目完成，若subagent未完成任务则继续驱动subagent完成
  3. 所有项目最新日志均为 `Review` passed 后，在 `develop` worktree merge其他项目的成功。

3.**验收成果**
  1. 更新文档
  2. 在根 `log.md` 顶部新增集成日志
  4. 启动总体验收 review subagent。并将验收结果补充到log.md，
  5. 若验收成功，将根任务和相关项目任务的 `Status` 改为 `completed`
  6. 进行一次commit提交
  7. 若验收失败，从**完成计划**的2.重新开始
