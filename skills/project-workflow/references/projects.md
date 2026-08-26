# Projects

本参考定义 `project-workflow` 的项目拆分文件格式。

## 文件名

项目拆分文件名为：

```text
.workflow/.projects
```

## 文件格式

```text
apps/web
services/api
```

每一行写一个 `<project-path>`。空行忽略，`#` 开头的行作为注释忽略。

有效的 `<project-path>` 必须是规范化的 worktree 相对路径：不得是绝对路径，不得包含空组件、`.` 或 `..`，不得以 `/` 结尾，也不得逃出 worktree。有效行之间不得重复。

## 规则

如果 `.workflow/.projects` 不存在或内容为空，先询问用户哪些项目目录允许单独创建 worktree/subagent，再将对应 `<project-path>` 按一行一个写入该文件。存在无效或重复路径时先停止并修正，不得据此创建 worktree 或分派 subagent。

新增允许单独拆分的项目时，只在 `develop/<project-path>` 创建委派所需的最小项目骨架，例如项目目录、manifest 和占位 README；不得在 workspace 根目录直接创建 `apps/`、`packages/`、`crates/` 等 monorepo 目录，也不得实现业务逻辑、功能代码或测试细节。
