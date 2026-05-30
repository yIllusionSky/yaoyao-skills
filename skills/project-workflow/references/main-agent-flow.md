# Main Agent Flow

本参考定义任务编排协议，包括任务记录、项目拆分、worktree 编排、子 agent 启动、主集成和总体验收。

## 工作区初始化

1. 工作范围是 `develop/`，后续主集成、根配置、跨项目检查都在 `develop` worktree 中执行。
2. 如果 `develop/` 不存在，从 `main/` 创建：

```bash
git -C main worktree add ../develop develop
```

3. 如果 `main/` 不存在或不可用，停止并报告缺少 main worktree。


## 工作流程

### 完成计划

1. 若不存在工作区，参考“工作区初始化”。
2. 确定本次任务使用的 `<task-id>`。
3. 根据用户需求或总体验收 review 反馈，在 `develop/.workflow/<task-id>/` 创建或更新根 `task.md` 和 `log.md`。
4. 分析是否需要额外创建独立项目，例如前端、后端、`crates/<name>`、`packages/<name>`。
5. 需要新增独立项目时，先在 `develop` 中初始化项目结构。
6. 为每个需要独立实现的项目创建或更新 `develop/.workflow/<task-id>/<project-worktree>/task.md` 和 `log.md`。

### 准备环境

1. 项目 worktree 使用固定路径 `<project-worktree>/`，同一个项目在不同任务中复用同一个项目级 worktree。
2. `<project-worktree>` 由项目相对路径归一化得到：去掉结尾 `/`，把 `/` 替换为 `-`。

```text
crates/auth -> crates-auth/
```

3. 项目 worktree 不存在时，从 `develop` 分支创建：

```bash
git -C develop worktree add --detach ../<project-worktree> develop
```

4. 在 `<project-worktree>/.skills` 写入该项目需要使用的技能名，每行一个；`.gitignore` 忽略 `.skills`。

### 执行和集成

1. 同一轮内为所有需要独立实现的项目创建 implementation subagent；必须先全部创建，再等待结果，不得创建一个就等待一个。
2. 创建 implementation subagent 时，必须告诉对方“你是 implementation subagent”，并告知它负责的 `project-worktree` 和 `workflow/<task-id>/<project-worktree>`。
3. 每个 implementation subagent 完成实现、自测和 commit 后，main agent 立即在 `develop` 中 merge 该项目任务分支；不要等所有 subagent 都完成后再统一 merge。

```bash
git -C develop merge --no-ff workflow/<task-id>/<project-worktree>
```

4. merge 冲突属于集成阶段问题，由 main agent 在 `develop` 中解决并记录。
5. 所有项目任务分支都 merge 到 `develop` 后，进入总体验收。

### 总体验收

1. 在 `develop` 中处理文档、根配置和跨项目检查。
2. 创建 review subagent，审查对象必须是 `develop` worktree 当前状态，包括已 merge 的项目改动、根配置、文档和跨项目集成结果。
3. main agent 将总体验收结果写入根 `log.md`。
4. 验收通过后，将根任务和相关项目任务的 `Status` 改为 `completed`。
5. 在 `develop` 提交最终 commit。
6. 验收失败时，回到“完成计划”第 3 步，再严格按本流程继续。
