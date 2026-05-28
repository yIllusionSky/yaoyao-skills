---
name: project-workflow
description: 项目初始化和大功能实现工作流技能。用于串联 GitHub Actions、Rust 架构、长期项目文档、GitHub issue、branch、PR、changelog、crate 级 subagent 实现、独立 review 和 issue 验收核对。
---

# Project Workflow

用于规划和执行项目初始化、大功能实现和验收闭环。除固定技术词、命令、文件名、crate、workspace、subagent 外，使用中文；不要使用模糊简称。

本技能只编排流程，不复制依赖技能的详细规则。执行对应步骤时必须使用或读取对应依赖技能。

## 依赖技能

依赖这些技能：

- `github-actions`
- `rust-architecture`
- `project-docs`
- `git-workflow`
- `changelog`

使用依赖技能时，优先按运行环境中可用的 `$skill-name` 触发。如果依赖技能未在运行环境中列出，但当前仓库存在 `skills/<skill-name>/SKILL.md`，必须先读取该文件再执行对应规则。如果依赖技能既不可用也找不到本地 `SKILL.md`，必须报告缺失依赖，不能凭记忆或猜测执行。

创建 subagent 时，主 agent 必须在任务说明中写明需要遵守的技能名称；工具支持传递 skill item 时，传递对应技能，否则传递必要的规则摘要和本地路径。

## 项目初始化

创建或初始化项目时按顺序执行：

1. 根据项目类型使用 `github-actions` 创建或维护 GitHub Actions workflow。
2. 使用 `rust-architecture` 选择最小够用的 Rust 项目结构和 crate 边界。
3. 使用 `project-docs` 创建或维护 README、ARCHITECTURE、features、operations 和子项目 README。

后续实现必须遵守已生成的架构和长期文档。当架构、入口、配置、功能行为或运行方式变化时，同步更新对应文档。

## 大功能实现

实现大功能时按顺序执行：

1. 使用 `git-workflow` 创建 GitHub issue。issue 必须包含目标、背景、验收标准和范围边界。
2. 从 `main` 创建工作分支，不在空分支上创建 PR。
3. 确认 CI workflow 已存在。提交或合并前按 `git-workflow` 和 `changelog` 要求检查 CI 与 changelog。
4. 按 crate 边界拆分实现任务，先处理子项目 crate，再处理主项目 crate 或根项目集成层。
5. 第一批已 review、已测试的有效变更 commit 后，创建 draft PR。PR 正文必须包含 `Closes #<issue>`。
6. 如果仓库不支持 draft PR，在第一批已 review、已测试的有效变更 commit 后创建普通 PR。
7. issue-check 和 CI 通过后，将 draft PR 标记为 ready。仓库使用普通 PR 时，确认 PR 已满足合并条件。

## Crate 实现顺序

默认 `crates/<crate-name>` 下的子项目 crate 互不依赖，只有主项目 crate 或根项目集成层依赖它们。

- 先为每个需要修改的独立子项目 crate 创建 worker subagent；多个互不依赖的子项目 crate 可以并行修改。
- 每个 worker 只能修改分配给它的 crate 目录和任务说明中逐项列出的额外文件路径。
- workspace member crate 修改 Rust 代码后，先使用 `cargo fmt -p <package>` 格式化该 crate，再使用 `cargo check -p <package>` 和 `cargo test -p <package>` 检查该 crate 的代码、单元测试和集成测试。
- 非 workspace member crate 修改 Rust 代码后，先使用 `cargo fmt --manifest-path crates/<crate-name>/Cargo.toml` 格式化该 crate，再使用 `cargo check --manifest-path crates/<crate-name>/Cargo.toml` 和 `cargo test --manifest-path crates/<crate-name>/Cargo.toml` 检查该 crate 的代码、单元测试和集成测试。
- worker 不能运行 `cargo test --workspace`、`cargo check --workspace` 或全仓格式化命令，不能修改根配置、主项目 crate、其他子项目 crate 或文档。
- 所有子项目 crate 修改、格式化、检查和 review 通过后，主 agent 再修改主项目 crate 或根项目集成层。
- 如果 `Cargo.toml` 显示子项目 crate 之间存在依赖，必须按依赖顺序处理：先修改被依赖 crate，再修改依赖它的 crate。
- 如果发现子项目 crate 之间存在循环依赖，停止实现并报告架构问题。

主项目 crate 或根项目集成层负责聚合、编排和调用子项目 crate。只有到主项目集成阶段，才允许运行跨 crate 检查、全 workspace 测试或修改根配置；修改范围仍必须服务于当前 issue。

## Subagent 规则

当前运行环境提供 subagent 能力时，必须使用 subagent。没有 subagent 工具时，必须明确说明降级，并由主 agent 本地执行同等实现、review 和 issue-check 步骤，不能声称完成了 subagent 验证。

worker subagent 任务说明必须包含：

- 负责的 crate 或文件范围。
- 不允许修改的范围。
- 具体功能要求。
- 允许执行的完整检查和测试命令。
- 需要遵守的技能名称或本地技能路径。

worker 完成后，创建独立 review subagent，只按下发给 worker 的功能要求审查实现正确性。worker review 通过后，由主 agent 集成已通过的子项目 crate 改动。

如果功能不需要修改主项目 crate 或根项目集成层，主 agent 可以在 worker review 通过后 commit。如果功能需要修改主项目 crate 或根项目集成层，主 agent 完成主集成改动后，必须创建独立 review subagent 审查主集成改动；主集成 review 通过后，主 agent 才能 commit。

commit 后创建独立 issue-check subagent，按 GitHub issue 的验收标准核对是否完成。issue-check 未通过时，主 agent 根据返回问题重新拆分修复任务：问题属于某个子项目 crate 时，创建该 crate 的 worker subagent；问题属于主项目 crate 或根项目集成层时，由主 agent 修改。修复后重复 review、commit、issue-check，直到满足 issue 要求。
