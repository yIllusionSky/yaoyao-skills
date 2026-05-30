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

必须按下面阶段从上到下执行；上一阶段未完成前不得进入下一阶段。

### 阶段 1：完成计划

1. 若不存在工作区，参考“工作区初始化”。
2. 确定本次任务使用的 `<task-id>`。
3. 根据用户需求或总体验收 review 反馈，在 `develop/.workflow/<task-id>/` 创建或更新根 `task.md` 和 `log.md`。
4. 分析是否需要额外创建独立项目。项目指 monorepo 中可独立实现、测试或委派的子目录，例如 `apps/<name>`、`crates/<name>`、`packages/<name>`。
5. 需要新增独立项目时，先在 `develop` 中初始化项目结构。
6. 为每个需要独立实现的项目创建或更新 `develop/.workflow/<task-id>/<project-worktree>/task.md` 和 `log.md`。

### 阶段 2：准备项目 worktree

1. 检查每个需要独立实现的项目是否存在对应 `<project-worktree>/`。
2. 若不存在，则创建该项目 worktree，并写入 `<project-worktree>/.skills`：

```bash
git -C develop worktree add --detach ../<project-worktree> develop
```

`<project-worktree>` 由项目相对路径归一化得到：去掉结尾 `/`，把 `/` 替换为 `-`，例如 `crates/auth` -> `crates-auth`。
`.skills` 每行一个技能名；`.gitignore` 忽略 `.skills`。

### 阶段 3：执行和集成

1. 创建阶段：同一轮内为所有需要独立实现的项目创建 implementation subagent；创建阶段未完成前，不得等待任何 subagent。创建时必须告诉对方“你是 implementation subagent”，并告知它负责的 `project-worktree` 和 `workflow/<task-id>/<project-worktree>`。
2. 等待和集成阶段：所有 implementation subagent 创建完成后才开始等待结果；任一 subagent 完成实现、自测和 commit 后，立即在 `develop` 中 merge 对应项目分支。

```bash
git -C develop merge workflow/<task-id>/<project-worktree>
```

如有冲突，在本次 merge 中解决。

3. 所有项目任务分支都 merge 到 `develop` 后，进入总体验收。

### 阶段 4：总体验收

1. 在 `develop` 中处理文档、根配置和跨项目检查。
2. 创建 review subagent，审查对象必须是 `develop` worktree 当前状态，包括已 merge 的项目改动、根配置、文档和跨项目集成结果。
3. 根据 review 结果更新根 `log.md` 和相关 `task.md`。
4. 在 `develop` 提交 commit。
5. 验收失败时，回到“阶段 1：完成计划”第 3 步，再严格按本流程继续。
