# TypeScript + Rust Monorepo

用于同一仓库同时包含 Bun workspace 与 Cargo workspace 的项目。monorepo 只统一所有权、依赖方向和仓库级验证，不要求所有应用使用同一种内部架构，也不为目录对称创建空的 TypeScript 或 Rust 项目。

## 业务优先布局

可部署应用先按业务能力归组，语言是业务目录内部的实现选择：

```text
.
├── apps/
│   ├── learning/
│   │   ├── api/                 # Rust 后端
│   │   └── web/                 # TypeScript 应用
│   └── identity/
│       ├── service/             # Rust 服务
│       └── admin/               # TypeScript 应用
├── packages/
│   ├── ui/                      # 跨业务 TypeScript package
│   └── api-client/              # 生成或手写的稳定客户端
├── crates/
│   ├── telemetry/               # 跨业务 Rust capability crate
│   └── third-party-client/
├── contracts/                   # 跨语言稳定契约及生成来源
├── Cargo.toml
├── Cargo.lock
├── package.json
└── bun.lock
```

- `apps/<business>/<app>` 放可部署、可独立运行或有明确产品入口的应用。业务只有一种语言时只创建实际存在的应用。
- 业务专属的 package、crate、fixture 或生成代码留在该业务目录；不要为了目录整齐提前上移。
- `packages/` 只放被多个业务真实使用的 TypeScript package，`crates/` 只放被多个业务真实使用的 Rust crate。禁止建立没有明确所有权的全局 `common`、`shared` 或 `utils` 桶。
- 每个 Rust 后端自行选择最小够用的结构；复杂后端遵守本技能的四类边界。TypeScript 应用按自身 UI、server 或 library 职责组织，不套 Rust 目录。

## Workspace 与依赖

- 根 `Cargo.toml` 明确列出 Rust workspace members；混合目录下的 glob 必须只匹配真实 crate。共用 package metadata、dependency version 和 lint 时使用对应 workspace 配置。
- Cargo workspace 使用根 `Cargo.lock`。只有确实需要脱离父 workspace 独立构建和发布的 Rust 项目才保留独立锁文件与自包含依赖。
- 根 `package.json` 设置 `private: true`、精确的 `packageManager: "bun@<version>"`、实际 workspace 路径，以及仓库级 `lint`、`typecheck`、`test`、`build` scripts；提交单一根 `bun.lock`。
- Bun workspace 内部依赖使用 `workspace:*`。只有具备独立发布、安装和生命周期边界的嵌套项目才拥有自己的 lockfile；不得因目录嵌套自然产生多套依赖树。
- 可部署应用不得依赖另一个应用的内部源码。应用可以依赖稳定 package/crate，package 与 crate 不反向依赖 `apps/`。
- 共享能力只有在至少两个真实消费者、稳定职责和明确所有者同时存在时才提取；单纯消除少量重复不能自动覆盖业务边界。

## 跨语言边界

- TypeScript 与 Rust 通过 HTTP、事件、命令或其他明确运行时协议交互，不通过相对路径读取对方内部源码或构建产物。
- 跨语言 request、response、event 和错误结构以稳定契约为来源。生成 client 或类型时记录生成命令与来源，不在生成文件中混入手写业务逻辑。
- 不直接把 Rust domain entity 或 TypeScript UI model 当作跨语言契约。边界 adapter 负责在契约类型与应用/domain 类型之间转换。
- 契约变化必须检查生产者、消费者、兼容策略和生成结果；只有一个语言使用的内部类型不进入全局 `contracts/`。

## 工具链与仓库命令

- `rust-toolchain.toml` 与旧式 `rust-toolchain` 都是可选的项目配置，不是 monorepo 前置条件。已有配置时服从其中的 channel；没有时按项目 CI 约定选择，默认可使用 `stable`。
- Cargo manifest 的 `rust-version` 表达 MSRV，不把它当作 CI toolchain pin。
- Bun 版本以根 `package.json` 的精确 `packageManager` 为仓库来源，不在每个 workspace 重复声明。
- 根脚本只负责编排 workspace，不容纳业务实现；单个应用仍保留可独立执行的本地 check、test 和 build 命令。

## CI 与发布

- pull request 默认分别运行完整 Cargo workspace 与 Bun workspace 检查。Rust 执行 fmt、clippy、test；TypeScript 使用 `bun ci` 后执行根 `lint`、`typecheck`、`test`、`build` scripts。
- 不默认对 Rust 使用 `--all-features`；先确认 feature 能同时启用，否则按项目声明的 feature matrix 验证。
- 只有仓库具备可靠的 workspace 依赖图和变更范围计算时才执行 affected-only；同时保留定期或合并前全量验证，避免遗漏跨业务和跨语言契约影响。
- 发布以可部署应用为单位。tag 或 workflow input 必须能唯一识别应用与版本；不要因为代码位于同一仓库就强制所有应用共用版本。
- GitHub Actions asset 与复制规则由 `github-actions` 技能维护；架构设计只规定检查边界，不复制另一份 workflow 实现。
