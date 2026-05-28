---
name: github-actions
description: 创建或维护 GitHub Actions workflow；按项目类型套用 CI、release、Docker assets 和复制脚本。
---

# GitHub Actions

用于创建或更新 `.github/workflows/*.yml`。优先使用 `scripts/copy_assets.py` 从 `assets/` 复制最接近的文件，asset 内容是执行规则的来源；除非用户明确要求，不要重写 workflow 逻辑。

说明文字使用中文；GitHub Actions 字段、命令、文件名和固定关键词保持原文。

## 复制 assets

在目标项目根目录执行复制脚本；脚本只复制文件，不运行安装、构建、格式化或其他项目命令。默认不覆盖已有文件，需要覆盖时显式传 `--force`。

```bash
python3 <skill-path>/scripts/copy_assets.py <ci|app|tauri|docker> --target <project-root>
```

复制规则：

- `ci`：复制 [ci.yml](./assets/ci.yml) 到 `.github/workflows/ci.yml`。
- `app`：复制 [app-release.yml](./assets/app-release.yml) 到 `.github/workflows/app-release.yml`。
- `tauri`：复制 [tauri-release.yml](./assets/tauri-release.yml) 到 `.github/workflows/tauri-release.yml`。
- `docker`：复制 [docker-release.yml](./assets/docker-release.yml) 到 `.github/workflows/docker-release.yml`，并复制 [docker assets](./assets/docker/) 到目标项目根目录。
