---
name: github-actions
description: 创建或维护 Rust 项目及 TypeScript + Rust monorepo 的 GitHub Actions CI、Docker release 与部署资产，以及独立项目的 app、Tauri 2 和 Docker tag release workflow；用于 `.github/workflows/*.yml`、Dockerfile、compose 和复制脚本。
---

# GitHub Actions

workflow 和部署配置遵守对应 assets 的实现规则。需要复制文件时使用 `scripts/copy_assets.py`；修改前读取目标项目的实际命令和配置，只调整本次任务涉及的部分。

- 说明文字使用中文；GitHub Actions 字段、命令、文件名和固定关键词保持原文。
- Docker assets 只提供部署配置，不创建 Rust、Tauri 或 frontend 应用源码。
- 复制前验证目标项目和全部冲突；验证失败时不写入任何文件。
- 默认不覆盖已有文件；只有用户明确要求时使用 `--force`。
- release workflow 先创建 draft，所有平台产物成功上传后再公开发布。
- monorepo 任务读取 [monorepo](./references/monorepo.md)，使用 `assets/monorepo/` 中与独立项目隔离的 workflow 和 Docker 资产。

## 复制命令

复制脚本要求 Python 3.11+。在目标项目根目录外或任意目录执行：

```bash
python3 <skill-path>/scripts/copy_assets.py ci --target <project-root>
python3 <skill-path>/scripts/copy_assets.py monorepo-ci --target <project-root>
python3 <skill-path>/scripts/copy_assets.py monorepo-release --target <project-root> --rust-package <package> --rust-bin <binary> --typescript-package <package> --typescript-app <relative-path>
python3 <skill-path>/scripts/copy_assets.py app --target <project-root> --app-bin <binary-name>
python3 <skill-path>/scripts/copy_assets.py tauri --target <project-root>
python3 <skill-path>/scripts/copy_assets.py docker --target <project-root> --server-bin <binary-name> [--with-client]
```

前置条件：

- `ci`、`app`：目标根目录存在 `Cargo.toml`。
- `monorepo-ci`：根 `Cargo.toml` 定义 workspace；根 `package.json` 设置 `private: true`、精确 `bun@X.Y.Z` 的 `packageManager`、非空 `workspaces`，并定义 `lint`、`typecheck`、`test`、`build` scripts；同时存在根 `bun.lock`。
- `monorepo-release`：满足 monorepo CI 前置条件，同时存在根 `Cargo.lock` 与 `CHANGELOG.md`；目标 TypeScript package 必须属于根 Bun workspace，名称匹配参数并定义 `build`、`start` scripts，构建结果为自包含 `dist/`。
- `tauri`：存在 `package.json`、`bun.lock` 和 `src-tauri/Cargo.toml`，且 `@tauri-apps/cli` 与 Rust `tauri` 依赖的 major version 都是 2。
- `docker`：`server` 是可以离开父 workspace 单独构建的 crate，存在 `server/Cargo.toml` 和 `server/Cargo.lock`，不使用 workspace 继承或指向 `server/` 外部的 path dependency。
- `docker --with-client`：除 server 前置条件外，存在 `client/package.json` 和 `client/bun.lock`，并显式依赖 `@sveltejs/adapter-node`，`build` 脚本产生 `build/index.js`。

workflow 变更后，按目标项目实际命令审查并运行 `actionlint`。Action 使用完整 commit SHA 固定版本，并在同行注释精确 release tag；没有 release tag 的 toolchain action 注释固定 channel。
