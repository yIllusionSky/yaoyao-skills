---
name: github-actions
description: 创建或维护 Rust 项目及 TypeScript + Rust monorepo 的 GitHub Actions CI、app、Tauri 2 和 Docker tag release workflow；用于 `.github/workflows/*.yml`、release assets、Dockerfile、compose 和复制脚本。
---

# GitHub Actions

优先使用 `scripts/copy_assets.py` 复制最接近的 asset。asset 是执行规则来源；除非用户明确要求，不要从头重写 workflow。

- 说明文字使用中文；GitHub Actions 字段、命令、文件名和固定关键词保持原文。
- Docker assets 是已有项目的部署叠加层，不创建 Rust、Tauri 或 frontend 应用源码。
- 复制前验证目标项目和全部冲突；验证失败时不写入任何文件。
- 默认不覆盖已有文件；只有用户明确要求时使用 `--force`。
- release workflow 先创建 draft，所有平台产物成功上传后再公开发布。
- monorepo CI 默认分别验证完整 Cargo 与 Bun workspace；只有项目具备可靠的依赖图和受影响范围计算时才缩小检查，并保留定期全量验证。

## 复制命令

复制脚本要求 Python 3.11+。在目标项目根目录外或任意目录执行：

```bash
python3 <skill-path>/scripts/copy_assets.py ci --target <project-root>
python3 <skill-path>/scripts/copy_assets.py monorepo-ci --target <project-root> [--rust-toolchain <specifier>]
python3 <skill-path>/scripts/copy_assets.py app --target <project-root> --app-bin <binary-name>
python3 <skill-path>/scripts/copy_assets.py tauri --target <project-root>
python3 <skill-path>/scripts/copy_assets.py docker --target <project-root> --server-bin <binary-name> [--with-client]
```

前置条件：

- `ci`、`app`：目标根目录存在 `Cargo.toml`。
- `monorepo-ci`：根 `Cargo.toml` 定义 workspace；根 `package.json` 设置 `private: true`、精确 `bun@X.Y.Z` 的 `packageManager`、非空 `workspaces`，并定义 `lint`、`typecheck`、`test`、`build` scripts；同时存在根 `bun.lock`。
- `tauri`：存在 `package.json`、`bun.lock` 和 `src-tauri/Cargo.toml`，且 `@tauri-apps/cli` 与 Rust `tauri` 依赖的 major version 都是 2。
- `docker`：`server` 是可以离开父 workspace 单独构建的 crate，存在 `server/Cargo.toml` 和 `server/Cargo.lock`，不使用 workspace 继承或指向 `server/` 外部的 path dependency。
- `docker --with-client`：除 server 前置条件外，存在 `client/package.json` 和 `client/bun.lock`，并显式依赖 `@sveltejs/adapter-node`，`build` 脚本产生 `build/index.js`。

`monorepo-ci` 的 Rust toolchain 按 `--rust-toolchain`、已有 `rust-toolchain.toml`、已有 `rust-toolchain`、`stable` 的顺序选择；这些文件都不是必需项。TypeScript job 由根 `packageManager` 选择 Bun，并使用 `bun ci` 和四个根 scripts。发布仍以可部署应用为单位，本 asset 不强制整个 monorepo 统一版本。

复制完成后，按目标项目实际命令审查 workflow 并运行 `actionlint`。Action 使用完整 commit SHA 固定版本，并在同行注释精确 release tag；没有 release tag 的 toolchain action 注释固定 channel。
