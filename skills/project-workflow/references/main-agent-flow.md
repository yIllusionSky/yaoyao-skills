# Main Agent Flow

本参考定义任务编排协议，包括任务记录、项目拆分、worktree 编排、子 agent 启动、主集成和总体验收。

## 工作区初始化

1. 工作范围是 `develop/`,后续主集成、根配置、跨项目检查都在 `develop` worktree 中执行。
2. 如果 `develop/` 不存在，从 `main/` 创建：

```bash
git -C main worktree add ../develop develop
```

3. 如果 `main/` 不存在或不可用，停止并报告缺少 main worktree。

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

5. 每轮创建子 agent 前，将项目 worktree 切到 detached 的 `develop`：

```bash
git -C <project-worktree> switch --detach --force develop
```

6. 在 `<project-worktree>/.skills` 写入该项目需要使用的技能名，每行一个；`.gitignore` 忽略 `.skills`。

## 工作流程

1. **完成计划**
   1. 创建 `task-id`。`task-id` 表示一次任务包，不要求对应单一功能。
   2. 在 `develop/.workflow/<task-id>/` 创建或更新根 `task.md` 和根 `log.md`。
   3. 分析是否需要额外创建独立项目，例如前端、后端、`crates/<name>`、`packages/<name>`。
   4. 需要新增独立项目时，先在 `develop` 中初始化项目结构。
   5. 为每个需要独立实现的项目创建或更新 `develop/.workflow/<task-id>/<project-worktree>/task.md` 和 `log.md`。

2. **执行任务**
   1. 为每个项目准备对应 worktree，切到 detached 的 `develop`，写入 `.skills`。
   2. 创建子 agent 时，必须告诉对方“你是 subagent”，并告知它负责的 `project-worktree`、任务文件路径、`.skills` 路径和返回要求。
   3. 子 agent 在自己的 worktree 中更新 `.workflow/<task-id>/<project-worktree>/log.md` 和 `task.md`。
   4. 项目 review passed 后，将该项目 worktree 中通过 review 的改动合入 `develop`。
   5. 项目未完成或 review 未通过时，更新对应项目任务记录后重新创建子 agent。

3. **验收成果**
   1. 所有项目完成后，在 `develop` 中处理文档、根配置和跨项目检查。
   2. 启动总体验收 review 子 agent，并将验收结果写入根 `log.md`。
   4. 验收通过后，将根任务和相关项目任务的 `Status` 改为 `completed`。
   5. 在 `develop` 提交最终 commit。
   6. 验收失败时，按问题归属回到“完成计划”或“执行任务”。
