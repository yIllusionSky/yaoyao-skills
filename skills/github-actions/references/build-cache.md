# 构建缓存与发布

## 触发与缓存来源

CI 仅处理目标为 `main` 的 PR，在 workflow 的 `on.pull_request.branches` 中直接限制目标分支，不监听 push。已有 PR 更新提交仍通过 PR 事件重新检查；合并或直接 push 到 main 不额外运行 CI。release workflow 仅监听匹配 `v*.*.*` 的 tag push，校验实际版本和 changelog 后创建 draft、构建上传产物并公开发布。普通分支 push 不运行发布流程，也不额外预热发布构建。

GitHub 不允许不同 tag 互读缓存，PR merge ref 的缓存也不能供其他 PR 或发布使用。CI 缓存主要帮助同一 PR 的后续运行；发布缓存主要帮助同一 tag 重跑。模板不在 main 上构建，因此不会主动生成可跨 ref 读取的默认分支缓存。独立 cache scope 和 target key 不会绕过 ref 隔离；新 PR、新 tag、缓存过期或 Rust stable 更新后仍可能冷构建。

CI 取消同一 ref 的旧运行；tag 发布不取消正在运行的任务。模板不接入外部镜像仓库作为跨 tag 缓存，也不增加分支发布构建。

## Rust 与 Bun

App 和 Tauri 的 Rust cache key 显式包含目标架构，避免同一 macOS runner 上不同 target 共用缓存 key。Tauri 每个矩阵任务只安装本任务需要的 Rust target。

Tauri 和 monorepo CI 将 Bun 下载缓存放在 runner 临时目录，使用 OS、架构、Bun 版本与 `bun.lock` 哈希作为 key，并允许从同版本的旧 lockfile 缓存恢复。命中后仍执行冻结 lockfile 的依赖安装。`setup-bun` 缓存的是 Bun 可执行文件，不能替代包下载缓存。

## Docker

两个 Docker release 模板在临时目录生成 Bake JSON，用当前 checkout 的路径 context 在同一 runner 上构建独立镜像。普通 Docker 保持 server/client 两个 scope，monorepo 保持 monorepo-rust/monorepo-typescript 两个 scope，均导出 `mode=max` 缓存。server-only 不创建 client target。

tag 构建使用 Bake 的 `load: true` 将镜像加载到本机，再 `docker save` 和 `pigz` 压缩。保留 Release 的离线 `.tar.gz` 交付方式，不登录或推送 GHCR。独立镜像可并行构建，实际提速取决于 runner 的 CPU、内存和缓存传输耗时。

普通 Docker 归档从项目 Compose 导出不含 build 的运行配置，保留环境变量占位符和相对路径，`.env.example` 中的镜像名和 tag 更新为本次产物。部署时仍需按项目说明配置环境文件；归档不会携带本地 `.env`。

普通前端镜像使用 Bun 1.4.0：先在只包含 manifests 的层执行无脚本安装，复制源码后正常安装并构建，最后用 `bun prune --production` 裁剪开发依赖。这样保留生产依赖在安装和构建期间生成的文件；不要用在已有 node_modules 上再次执行 `bun install --production` 代替裁剪。运行所需的外部依赖必须声明在 dependencies，项目专属的额外运行文件需补充明确的 COPY。

monorepo TypeScript 仍按目标项目的 packageManager 固定 Bun，并遵守自包含 dist 的约定。monorepo 保留完整源码 context，不通过猜测跨语言依赖缩小 COPY。npmrc 继续使用 BuildKit secret，Bake 定义只存 secret 的环境变量名称。

## 验证

修改后运行仓库技能校验与 actionlint，并验证 CI 仅监听面向 main 的 PR、release 仅监听版本 tag、产物失败不会公开 draft、无 checkout 的发布命令显式指定仓库。Docker 变更还要检查冷缓存和热缓存构建、运行镜像启动及归档完整性。记录构建与压缩耗时、镜像体积，跨 ref 缓存命中以实际 GitHub Actions 日志为准。
