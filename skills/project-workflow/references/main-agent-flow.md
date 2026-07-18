# Main Agent Flow

本参考定义非 team 本地任务编排协议。执行前必须读取 `workspace-layout.md`、`task-format.md`、`projects.md` 和 `commit.md`。

## 工作区初始化

1. 确认当前目录是用户指定的专用 workspace，且符合 `workspace-layout.md`。不要因为缺少 `main/` 就在已有项目目录内创建嵌套仓库。
2. `main/` 不存在时，仅在专用 workspace 没有无法确认用途的项目内容时初始化：

```bash
mkdir main
git -C main init -b main
git -C main commit --allow-empty -m "chore: 初始化 main 基线"
```

3. `develop/` 是 detached 集成 worktree，不要求存在同名分支。不存在时从 `main` 创建：

```bash
git -C main worktree add --detach ../develop main
```

## 阶段 1：计划和任务分支

1. 确认 `develop/` 工作区干净；存在改动时先判断来源，不覆盖或丢弃。
2. 确定唯一的 `<task-id>`。已有同名任务且不是继续执行时，按 `task-format.md` 生成新名称。
3. 已有任务分支时直接切换；新任务先回到 detached `main` 基线，再创建分支，禁止从上一个任务分支派生：

```bash
git -C develop switch --detach main
git -C develop switch -c <task-id>
```

4. 读取 `.workflow/.projects`。只有列出的 `<project-path>` 可以创建独立 worktree 和 implementation subagent。
5. 创建或更新根 `task.md`、项目 `task.md` 和对应 `log.md`，明确 `project-path`、`project-worktree`、`Allowed Paths`、验收标准和测试计划。
6. 同一个共享文件或公共接口只分配给一个 implementation subagent；其他项目通过已约定接口协作。
7. 提交任务记录和委派所需的最小项目骨架，确保项目 worktree 能读取相同基线。

## 阶段 2：准备项目 worktree

对每个项目执行：

1. 不存在时从 `<task-id>` 创建 detached worktree：

```bash
git -C develop worktree add --detach ../<project-worktree> <task-id>
```

2. 已存在时验证它属于同一 Git 仓库、工作区状态可解释，并且没有其他任务的未完成改动；无法确认时停止，不复用该目录。
3. 写入 `<project-worktree>/.skills`，每行一个必要 skill 名；`.gitignore` 必须忽略该文件。

## 阶段 3：分批执行和集成

1. 根据当前可用 agent slot 启动第一批 implementation subagent，不超过可用容量；项目数超过容量时保留等待队列。
2. 任一 subagent 完成实现、自测和 commit 后，立即在 `develop/` 的 `<task-id>` 分支 merge 对应分支：

```bash
git -C develop merge workflow/<task-id>/<project-worktree>
```

3. 一个 slot 释放后再启动下一个等待项目，直到全部完成。不要要求所有项目都 spawn 后才开始等待。
4. merge conflict 由 main agent 在当前 merge 中处理；项目实现问题重新派回对应 implementation subagent，main agent 不替代其实现。
5. 全部项目 merge 后完成根配置、长期文档、跨项目引用和整体测试入口等根级集成，并记录到根 `log.md`。

## 阶段 4：总体验收和交付

1. 启动 review subagent，审查 `<task-id>` 相对 `main` 的完整变化、授权路径、记录和测试覆盖。
2. 有 finding 时更新任务记录，并重新派给对应 implementation subagent；修复后重新集成和 review。
3. review 通过后更新状态和日志，在 `<task-id>` 分支提交最终记录。
4. 确认 `develop/` 当前分支仍为 `<task-id>` 且工作区干净，向用户交付该任务分支；不自动 merge `main`、push 或创建 PR。
5. 默认保留项目 worktree 和任务分支，只在结果中列出可清理项；未经用户要求不删除。
