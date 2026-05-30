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

**完成计划**

1. 若不存在工作区，参考工作区初始化
2. 创建 `task-id`
3. 根据用户的需求或者review的反馈在 `develop/.workflow/<task-id>/` 创建或更新根 `task.md`。
4. 分析是否需要额外创建独立项目，例如前端、后端、`crates/<name>`、`packages/<name>`。
5. 需要新增独立项目时，先在 `develop` 中初始化项目结构。
6. 为每个需要独立实现的项目创建或更新 `develop/.workflow/<task-id>/<project-worktree>/task.md`。

**准备环境**

7. 项目 worktree 不存在时，从 `develop` 分支创建：

```bash
git -C develop worktree add --detach ../<project-worktree> develop
```

其中项目目录名由项目相对路径归一化得到：去掉结尾 `/`，把 `/` 替换为 `-`。

```text
crates/auth -> crates-auth/
```

随后在 `<project-worktree>/.skills` 写入该项目需要使用的技能名，每行一个；`.gitignore` 忽略 `.skills`。


8. 每轮创建子 agent 前，先检查项目 worktree 是否有未合入改动：

```bash
git -C <project-worktree> status --short
```

如果存在输出，对该未合并的改动进行处理，判断是之前子agent未完成还是别的原因，如果未完成驱动子agent完成该任务并合并。如果是未提交，则提交后合并

9. 项目 worktree 干净时，将它切到 detached 的 `develop`：

```bash
git -C <project-worktree> switch --detach develop
```

**执行任务**

10. 根据每个需要开发的worktree创建 并行的implementation subagent 时，必须告诉对方“你是 implementation subagent”，并告知它负责的 `project-worktree`、`<task-branch>`。
11. implementation subagent 执行成功后，在 `develop` 中 merge 该项目任务分支：

```bash
git -C develop merge --no-ff <task-branch>
```

对于有冲突的地方，进行解决。

**验收成果**

11. 所有项目完成后，在 `develop` 中处理文档、根配置和跨项目检查。
12. 创建 review subagent，审查对象必须是 `develop` worktree 当前状态，包括已 merge 的项目改动、根配置、文档和跨项目集成结果。
13. main agent 将总体验收结果写入根 `log.md`。
14. 验收通过后，将根任务和相关项目任务的 `Status` 改为 `completed`。
15. 在 `develop` 提交commit。
16. 验收失败时，返回到第3步。验收成功则推出任务
