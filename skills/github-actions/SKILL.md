---
name: github-actions
description: 创建或维护 Rust 项目的 GitHub Actions CI、app/Tauri/Docker tag release workflow，并把 Docker 部署文件叠加到已有 server/client 项目。用于 `.github/workflows/*.yml`、release assets、Dockerfile、compose 和复制脚本。
---

# GitHub Actions

优先使用 `scripts/copy_assets.py` 复制最接近的 asset。asset 是执行规则来源；除非用户明确要求，不要从头重写 workflow。

- 说明文字使用中文；GitHub Actions 字段、命令、文件名和固定关键词保持原文。
- Docker assets 是已有项目的部署叠加层，不创建 Rust、Tauri 或 frontend 应用源码。
- 复制前验证目标项目和全部冲突；验证失败时不写入任何文件。
- 默认不覆盖已有文件；只有用户明确要求时使用 `--force`。

## 复制命令

在目标项目根目录外或任意目录执行：

```bash
python3 <skill-path>/scripts/copy_assets.py ci --target <project-root>
python3 <skill-path>/scripts/copy_assets.py app --target <project-root> --app-bin <binary-name>
python3 <skill-path>/scripts/copy_assets.py tauri --target <project-root>
python3 <skill-path>/scripts/copy_assets.py docker --target <project-root> --server-bin <binary-name> [--with-client]
```

前置条件：

- `ci`、`app`：目标根目录存在 `Cargo.toml`。
- `tauri`：存在 `package.json`、`bun.lock` 和 `src-tauri/Cargo.toml`。
- `docker`：存在 `server/Cargo.toml`；使用 `--with-client` 时还要存在 `client/package.json` 和 `client/bun.lock`。

复制完成后，按目标项目实际命令审查 workflow 并运行 `actionlint`。Action 使用完整 commit SHA 固定版本，并在同行注释对应 release tag。
