# Subagent Flow

本参考定义项目 subagent 和总体验收 review subagent 的执行协议。subagent 只按 main agent 任务说明第一段声明的角色和范围工作。

## Main Agent 下发要求

main agent 启动任何 subagent 时，任务说明必须包含：

- 第一段明确声明角色和范围。
- 对应根或项目 `task.md` 路径。
- 对应 `log.md` 路径。
- worktree 路径。
- 允许修改范围。

项目 subagent 的任务说明还必须包含 `.skills` 路径。

如果任务说明没有明确声明角色或范围，subagent 必须停止并要求 main agent 补充。

## 项目 Subagent

项目 subagent 使用任务说明中的项目 `task.md`、项目 `log.md` 和 worktree 路径工作。

项目 subagent 必须读取自己 worktree 中的 `.skills`，并按其中的技能名加载需要使用的技能；空文件表示无额外技能。

项目 subagent 只能修改：

- 自己所在项目 worktree。

项目 subagent 不能修改：

- 其他项目 worktree。
- `develop` 或 `main` worktree。
- worktree 配置或保留状态。

项目 subagent 完成后，必须在项目 `log.md` 的 `Work Log` 下最上方新增一条日志，写：

- `Changed`
- `Tests`
- `Review`

项目 subagent 的 `Review` 是自 review。自 review 未通过时，继续在同一项目 worktree 中修复；无法继续时，在最终答复中说明阻塞问题。

## 总体验收 Review Subagent

总体验收 review subagent 使用任务说明中的根 `task.md`、根 `log.md`、相关项目任务记录和 review 范围工作。

总体验收 review subagent 只审查，不实现，不写文件。

总体验收 review subagent 必须检查：

- 是否满足根 `task.md` 的 `Acceptance Criteria`。
- 是否执行或合理说明了根 `task.md` 的 `Test Plan`。
- 修改范围是否符合 main agent 下发的范围。
- 日志是否按 `task-format.md` 写入。

总体验收 review subagent 必须在最终答复中返回：

```markdown
Status: <changes requested|passed>

### Findings

-

### Required Rework

-
```

review 未通过时，必须列出可执行的返工问题，并说明问题归属到哪个项目或集成层。

## 最终答复

subagent 最终答复必须列出：

- 使用的技能；没有则写“无”。
- 已读取的任务文件。
- 修改过的文件路径；总体验收 review subagent 写“未修改文件”。
- 执行过的测试或检查。
- review 状态。
