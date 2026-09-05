# Monorepo GitHub Actions 与 Docker

用于根目录同时包含 Cargo workspace 与 Bun workspace 的仓库。monorepo 使用独立 assets，不能套用要求 `server/` 脱离父 workspace 构建的普通 Docker 资产。

## 资产边界

- `assets/monorepo/workflows/ci.yml`：单一仓库级 CI，分别运行完整 Rust 与 TypeScript workspace 检查。
- `assets/monorepo/workflows/release.yml`：使用仓库统一 `vX.Y.Z`，校验 Rust package、TypeScript package 和 changelog 版本后构建两个 Docker 镜像并发布一个归档。
- `assets/monorepo/docker/rust.Dockerfile`：以仓库根目录为 context，通过 Cargo package 与 binary 选择发布目标。
- `assets/monorepo/docker/typescript.Dockerfile`：以仓库根目录为 context，构建时递归复制 workspace manifests 与可选 `bunfig.toml`，通过 Bun package filter 建立无生命周期脚本的依赖缓存层；复制源码后再完成正常安装并构建目标 package。生产阶段只复制该应用的 `package.json` 与 `dist/`。
- `assets/monorepo/docker/docker-compose.yaml`：只让 Pingap 发布宿主机端口；Rust 和 TypeScript 只在 Compose 网络内 `expose`。
- `assets/monorepo/docker/docker-compose.release.yaml`：只引用已导出的镜像，不依赖 release 包中不存在的源码和 Dockerfile。

## CI

仅在目标为 `main` 的 PR 时于 Ubuntu 运行两个 job，不监听 push：

- Rust：workspace fmt、clippy、test，不默认启用全部 feature。
- TypeScript：`bun ci` 后执行根 `lint`、`typecheck`、`test`、`build` scripts。

不要为每个服务复制一套基础 CI。服务特有的数据库、协议或端到端测试作为同一 workflow 的额外 job；只有具备可靠依赖图时才缩小到 affected-only，并保留全量验证。

仓库不使用 `rust-toolchain.toml` 或 `rust-toolchain`；本地使用当前激活的 Rust，GitHub Actions 和 Docker builder 使用 `stable`。

## Release 与 Docker

第一版沿用仓库统一版本：Rust package 与 TypeScript package 的 `version` 必须同时匹配 tag。release workflow 构建 `<repository>-rust:<version>` 与 `<repository>-typescript:<version>`，把镜像、compose、Pingap 配置和环境文件打包到 draft release，成功后公开。

TypeScript 资产面向具有 `build` 与 `start` scripts、监听 3000 端口的 Bun server package。`build` 必须生成自包含的 `dist/`，`start` 必须只依赖生产镜像中的 `package.json`、`dist/` 和 Bun runtime；需要外置 `node_modules` 的 framework、静态 SPA、其他 runtime 或多个独立发布目标应单独扩展。Rust binary 监听 8080。

Rust 与 TypeScript 镜像分别使用 `monorepo-rust`、`monorepo-typescript` BuildKit cache scope。Rust builder 用 cargo-chef 缓存所选 package/bin 的依赖；TypeScript 依赖层使用 Docker `COPY --parents` 在每次构建时递归发现 manifests，先用 `--ignore-scripts` 完成可复用安装，复制源码后再正常执行 `bun ci`，因此 workspace 生命周期脚本可以读取源码。两个 production stage 都不得复制 builder 的工具链、源码树或构建缓存。

release workflow 仅在版本 tag push 时运行，通过 Bake 在同一 runner 上并行构建两个镜像，加载镜像后用 pigz 生成离线归档。GHA 缓存可供同一 tag 重跑使用，不同 tag 之间无法直接复用；模板不运行分支预热。完整规则见 [构建缓存](./build-cache.md)。

非敏感 Bun 安装配置使用仓库根 `bunfig.toml`。私有 registry 的 `.npmrc` 不进入 context、镜像层或 BuildKit cache：本地 Compose 通过 `NPMRC_PATH` 指向私有文件，release workflow 从可选的 GitHub Actions `NPMRC` secret 挂载；不需要认证时使用随资产复制的空示例文件。

Pingap 是整个部署栈唯一公网入口：

```text
/api/* -> rust:8080
/*     -> typescript:3000
```

示例只发布 HTTP 80，不声称已经提供 TLS。生产 HTTPS 应在 Pingap 中补充实际证书配置，或在更外层入口终止 TLS；未配置 HTTPS 时不得发布无监听者的 443。
