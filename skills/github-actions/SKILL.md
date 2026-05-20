---
name: github-actions
description: 创建或维护 GitHub Actions workflow；按项目类型套用 CI、release、Docker 模板。
---

# GitHub Actions

用于创建或更新 `.github/workflows/*.yml`。优先复制 `template/` 中最接近的文件，模板内容是执行规则的来源；除非用户明确要求，不要重写模板逻辑。

说明文字使用中文；GitHub Actions 字段、命令、文件名和固定关键词保持原文。

## 选择模板

- [ci](./template/ci.yml)：PR 检查。
- [app-release](./template/app-release.yml)：普通 Rust app 的 tag release。
- [tauri-release](./template/tauri-release.yml)：Tauri 桌面应用的 tag release。
- [docker-release](./template/docker-release.yml)：Docker 打包发布；同时使用 [docker template](./template/docker/) 里的配套项目模板。
