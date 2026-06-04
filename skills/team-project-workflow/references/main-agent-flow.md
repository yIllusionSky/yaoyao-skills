# Main Agent Flow

本参考定义任务编排协议，包括任务记录、项目拆分、worktree 编排、subagent 启动、主集成和总体验收。执行前必须先读取 `workspace-layout.md`、`task-format.md`、`projects.md` 和 `commit.md`。

## 工作区初始化

参考目录布局：

```text
workspace/
├── main/
├── develop/
│   ├── .workflow/
│   │   ├── .projects
│   │   └── <task-id>/
│   │       ├── task.md
│   │       ├── log.md
│   │       └── <project-worktree>/
│   │           ├── task.md
│   │           └── log.md
│   └── <project-path>/
└── <project-worktree>/
    ├── .skills
    └── <project-path>/
```

1. `main/` 是主基线 worktree；如果 `main/` 不存在，则创建 `main/` 并初始化 git 仓库：

```bash
mkdir main
git -C main init -b main
git -C main commit --allow-empty -m "chore: initialize main baseline"
```

2. `develop/` 是集成 worktree 目录，必须对应真实 `develop` 分支；后续主集成、根配置、跨项目检查都在 `develop/` 中执行。
3. 如果 `develop/` 不存在，先从 `main` 创建或使用真实 `develop` 分支，再创建 worktree：

```bash
git -C main worktree add -b develop ../develop main
```

如果 `develop` 分支已存在：

```bash
git -C main worktree add ../develop develop
```

## 工作流程

必须按下面阶段从上到下执行；上一阶段未完成前不得进入下一阶段。

### 阶段 1：完成计划

1. 若不存在 `develop/` worktree，参考“工作区初始化”。
2. 确定本次任务使用的 `<task-id>`。
3. 在 `develop/` 中创建或切换从 `develop` 基线派生的 `<task-id>` 集成分支；新建任务分支前先切回 `develop`：

```bash
git -C develop switch develop
```

再创建 `<task-id>`：

```bash
git -C develop switch -c <task-id>
```

如果分支已存在，切到该分支继续：

```bash
git -C develop switch <task-id>
```

4. 读取 `.workflow/.projects` 得到允许单独创建 worktree/subagent 的 `<project-path>` 列表；本次任务选中的项目必须来自该列表。未列入该文件的 package/crate/module 不创建独立 project worktree，也不单独分派 implementation subagent。需要修改未列入目录时，通过相关项目任务的 `Allowed Paths` 授权。
5. 根据用户需求或总体验收 review 反馈，在 `develop/.workflow/<task-id>/` 创建或更新根 `task.md`。
6. 每个需要独立实现的项目必须确定 `project-path`、`project-worktree` 和 `Allowed Paths`；`project-path` 是本次任务选中的项目路径，`project-worktree` 是外层 worktree 目录名，`Allowed Paths` 是该 subagent 除 workflow 记录外可修改的路径集合。
7. 为每个需要独立实现的项目创建或更新 `develop/.workflow/<task-id>/<project-worktree>/task.md`；项目 `task.md` 必须写明 `project-path` 和 `Allowed Paths`。
8. 同一个共享包如需被多个 subagent 修改，必须在各自任务中说明修改边界，避免重复修改同一文件或同一接口。
9. 计划、拆分文件和项目任务记录完成前，不得进入项目实现。
10. 阶段 1 产生的任务拆分文件和最小项目结构必须在 `<task-id>` 分支形成提交，确保后续项目 worktree 可以读取任务文件。

### 阶段 2：准备项目 worktree

1. 检查本次任务选中的每个 `<project-path>` 是否存在对应 `<project-worktree>/`。
2. 若不存在，则创建该项目 worktree，并写入 `<project-worktree>/.skills`：

```bash
git -C develop worktree add --detach ../<project-worktree> <task-id>
```

`<project-worktree>` 由 `<project-path>` 归一化得到：去掉结尾 `/`，把 `/` 替换为 `-`，例如 `apps/backend` -> `apps-backend`。
`.skills` 每行一个技能名；`.gitignore` 忽略 `.skills`。

### 阶段 3：执行和集成

1. 创建阶段：连续为本次任务选中的项目创建 implementation subagent；这些项目必须存在于 `.workflow/.projects`。所有 `spawn_agent` 调用完成前，禁止 `wait_agent`，禁止 main agent 修改任何项目任务授权路径下的文件。创建时必须告诉对方“你是 implementation subagent”，必须使用 `team-project-workflow`，读取 `workspace-layout`、`task-format`、`commit` 和 `implementation-subagent-flow`，并告知：
   - `project-worktree`
   - `project-path`
   - `Allowed Paths`
   - `workflow/<task-id>/<project-worktree>`
   - `.workflow/<task-id>/<project-worktree>/task.md`
   - `.workflow/<task-id>/<project-worktree>/log.md`
2. 等待和集成阶段：所有 implementation subagent 创建完成后才开始等待结果；任一 subagent 完成实现、自测和 commit 后，立即在 `develop/` 当前 `<task-id>` 分支中 merge 对应项目分支。

```bash
git -C develop merge workflow/<task-id>/<project-worktree>
```

如有冲突，在本次 merge 中解决。

3. main agent 只允许在 merge 冲突解决和根级集成阶段修改项目任务涉及路径、根配置、长期文档和 workflow 记录；不得替代 implementation subagent 直接实现项目任务。
4. 所有项目任务分支都 merge 到 `develop/` 的 `<task-id>` 分支后，先在 `develop/` 中完成根级集成处理，再进入总体验收。根级集成处理包括但不限于：
   - 根 `Cargo.toml`、workspace members、package 配置等根配置更新。
   - 检查本次用户或工程上有意义的变更是否已记录到 changelog，使用 `changelog` skill；未记录则补充记录。
   - 如果本次变更影响项目入口、目录结构、子项目职责、架构边界、功能行为、运行方式或配置，使用 `project-docs` skill 检查并更新长期文档。
   - 跨项目引用、构建入口、测试入口和整体命令检查。
5. 将根级集成处理结果记录到 `develop/.workflow/<task-id>/log.md`。

### 阶段 4：总体验收

1. 创建 review subagent，审查对象必须是 `develop/` 当前 `<task-id>` 分支状态，包括已 merge 的项目改动、根配置、文档和跨项目集成结果。创建时必须告诉对方“你是 review subagent”，必须使用 `team-project-workflow`，读取 `workspace-layout`、`task-format`、`commit` 和 `review-subagent-flow`。
2. 根据 review 结果更新根 `log.md` 和相关 `task.md`。
3. 提交 commit。
4. 验收失败时，回到“阶段 1：完成计划”第 3 步，再严格按本流程继续。
