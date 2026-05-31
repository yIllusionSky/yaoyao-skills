# Workspace Layout

本参考定义 `project-workflow` 的目录边界。所有角色必须先按本参考解释路径，再执行自己的 flow。

## 目录层级

workspace 根目录只允许出现：

- `main/`：主基线 worktree。
- `develop/`：集成 worktree 目录，当前分支是 `<task-id>`。
- `<project-worktree>/`：项目 implementation subagent 使用的独立 worktree。

workspace 根目录禁止直接创建 monorepo 项目路径或其一级父目录，例如：

- `apps/`
- `packages/`
- `crates/`
- 任何由 `<project-path>` 拆出的顶层目录。

如果 workspace 根目录出现上述禁止目录，必须先停止并报告布局违规，不得继续实现。

## 路径含义

- `<project-path>` 永远是 worktree 内的相对路径，例如 `apps/web`、`packages/ui`。
- main agent 操作项目结构时，`<project-path>` 对应 `develop/<project-path>`。
- implementation subagent 操作项目代码时，`<project-path>` 对应 `<project-worktree>/<project-path>`。
- `<project-worktree>` 永远是 workspace 根下的 worktree 目录名，由 `<project-path>` 去掉结尾 `/`，把 `/` 替换为 `-` 得到；例如 `apps/web` -> `apps-web`。

## 正确布局示例

```text
workspace/
├── main/
├── develop/
│   ├── .workflow/
│   │   └── <task-id>/
│   ├── apps/
│   │   └── web/
│   └── packages/
│       └── ui/
├── apps-web/
│   └── apps/
│       └── web/
└── packages-ui/
    └── packages/
        └── ui/
```

`apps/` 和 `packages/` 只能出现在某个 worktree 内，不能作为 workspace 根目录的直接子目录。
