# Main Agent Flow

以本地 `main` 为基线和最终集成目标；目录与任务字段遵守主 skill 引用的公共参考。

## 工作区初始化

1. 确认当前目录是用户指定的专用 workspace，且符合 `workspace-layout.md`。不要因为缺少 `main/` 就在已有项目目录内创建嵌套仓库。
2. `main/` 不存在时，仅在专用 workspace 没有无法确认用途的项目内容时初始化：

```bash
mkdir main
git -C main init -b main
git -C main commit --allow-empty -m "chore: 初始化 main 基线"
```

3. `develop/` 是承载当前任务分支的集成 worktree，不要求存在同名分支。目录不存在时从 `main` 创建 detached worktree：

```bash
git -C main worktree add --detach ../develop main
```

目录已存在时，验证它属于 `main/` 的同一 Git 仓库，且状态和当前任务可以解释；无法确认时停止，不复用该目录。

## 阶段 1：计划和任务分支

1. 确认 `main/` 当前分支为 `main` 且工作区干净；存在改动时先判断来源，不覆盖或丢弃。
2. 确认 `develop/` 工作区干净；存在改动时先判断来源，不覆盖或丢弃。
3. 确定唯一的 `<task-id>`。已有同名任务且不是继续执行时，按 `task-format.md` 生成新名称。
4. 已有任务分支时直接切换；新任务先回到 detached `main` 基线，再创建分支，禁止从上一个任务分支派生：

```bash
git -C develop switch --detach main
git -C develop switch -c <task-id>
```

5. 读取 `.workflow/.projects`。只有列出的 `<project-path>` 可以创建独立 worktree 和 implementation subagent；按 `task-format.md` 为每个项目确定唯一的 `<project-worktree>`。
6. 创建或更新根 `task.md`、项目 `task.md` 和对应 `log.md`，明确 `project-path`、`project-worktree`、`Allowed Paths`、验收标准和测试计划。
7. 同一个共享文件或公共接口只分配给一个 implementation subagent；其他项目通过已约定接口协作。
8. 确保仓库根 `.gitignore` 已忽略 `.skills`，然后提交任务记录、忽略规则和委派所需的最小项目骨架，确保项目 worktree 能读取相同且干净的基线。

## 阶段 2：准备项目 worktree

对每个项目执行：

1. 首次派发时，将当前 `<task-id>` 的完整 SHA 写入项目 `task.md` 的 `Base Commit` 并提交记录，再从任务分支准备 worktree。不存在时执行：

```bash
git -C develop worktree add --detach ../<project-worktree> <task-id>
```

2. 已存在时验证它属于同一 Git 仓库且没有其他任务的未完成改动；首次派发切到任务分支的 detached 基线，恢复任务保留原分支和进度。无法确认来源时不复用。
3. 写入 `<project-worktree>/.skills`，每行一个必要 skill 名。
4. 确认 `.skills` 已被忽略，连同项目路径、任务记录和 `Base Commit` 下发。恢复时按 implementation flow 处理已有修改，不因本任务安装生成的根锁文件修改停止。

## 阶段 3：分批执行和集成

1. 根据当前可用 agent slot 启动第一批 implementation subagent，不超过可用容量；项目数超过容量时保留等待队列。
2. 任一 subagent 完成实现、自测和 commit 后，立即在 `develop/` 的 `<task-id>` 分支 merge 对应分支：

```bash
git -C develop merge workflow/<task-id>/<project-worktree>
```

3. 一个 slot 释放后再启动下一个等待项目，直到全部完成。不要要求所有项目都 spawn 后才开始等待。
4. merge conflict 由 main agent 处理；项目实现问题重新派回 implementation subagent。需要同步项目基线时，先确认该 subagent 已停止修改 worktree 并保留未提交工作；已集成分支 fast-forward 到任务分支，来源明确的并行分叉则在项目分支合入任务分支，来源不明时调查。同步成功后，在项目记录和根日志中将 `Base Commit` 更新为本次合入的任务分支完整 SHA。
5. 全部项目 merge 后完成本任务涉及的根配置、长期文档和跨项目集成，正常安装依赖、更新根锁文件并运行整体测试；结果写入根 `log.md`，通过后提交集成结果。

## 阶段 4：总体验收和合并 main

1. 确认当前 `main` 是 `<task-id>` 的祖先：

```bash
git -C develop merge-base --is-ancestor main HEAD
```

如果 `main` 已前进，先在 `<task-id>` 中合入 `main`，处理冲突并重新运行必要测试，再进入 review。

2. 确认必要测试通过、全部待审改动已提交且 `develop/` 干净。将 `main` 的完整 SHA 作为 `Base Commit`、任务分支 HEAD 作为 `Reviewed Commit` 下发 review；审查期间不修改候选版本。
3. 项目实现 finding 派回对应 subagent；根配置、跨项目集成和根文档 finding 由 main agent 修复。修复后重新集成、验证并提交，再对新的候选版本 review。
4. review 通过后，只追加审查结果和更新完成状态，按 task format 记录两个 SHA 并提交。检查 `git -C develop diff <reviewed-commit> HEAD`：代码、配置、长期文档、授权路径或验收标准有变化时，补充验证并重新 review。
5. 确认两个 worktree 干净、`main/` 当前分支为 `main` 且 HEAD 仍等于审查基线；不一致时回到第 1 步重新同步和验收。一致时使用 merge commit 保留任务边界：

```bash
git -C main merge --no-ff <task-id>
```

6. 确认 `main/` 当前分支为 `main`、工作区干净且 `<task-id>` 已成为 `main` 的祖先。
7. 不自动 push。默认保留项目 worktree 和任务分支，只在结果中列出可清理项；未经用户要求不删除。
