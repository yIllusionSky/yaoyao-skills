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

每一行写一个 `<project-path>`，必须是 worktree 内的相对路径。空行忽略，`#` 开头的行作为注释忽略。

## 规则

如果 `.workflow/.projects` 不存在或内容为空，先询问用户需要拆分哪些项目，再将用户指定的 `<project-path>` 按一行一个写入该文件。
