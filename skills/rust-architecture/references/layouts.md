# Rust 项目布局示例

## 简单 CLI 或小工具

```text
src/
├── main.rs
├── cli.rs
├── core.rs
└── error.rs
```

- `main.rs`：只负责安装 `color-eyre`、解析 CLI、调用 `core` 入口。
- `cli.rs`：使用 `clap` 定义命令和参数。
- `core.rs`：核心执行逻辑和纯业务逻辑。
- `error.rs`：使用 `thiserror` 定义当前 crate 的错误类型。
- 不需要 `lib.rs`，除非同时要作为 library 被其他 crate 复用。

## 稍复杂 CLI 或小工具

```text
src/
├── main.rs
├── cli.rs
├── commands/
├── core/
├── adapters/
└── error.rs
```

- `main.rs`：初始化、安装 `color-eyre`、解析 CLI、分发命令。
- `cli.rs`：使用 `clap` 定义命令和参数。
- `commands/`：不同命令的执行入口。
- `core/`：核心逻辑和纯业务逻辑。
- `adapters/`：文件系统、网络、时间、外部命令等 IO 实现。
- `error.rs`：使用 `thiserror` 定义当前 crate 的错误类型。

## 普通 Library Crate

```text
src/
├── lib.rs
├── error.rs
├── types.rs
├── config.rs
└── client.rs
```

- `lib.rs` 控制 public API，不塞大量实现。
- `error.rs` 使用 `thiserror` 定义 crate 自己的结构化错误。
- `types.rs` 放公共类型。
- `config.rs` 和 `client.rs` 只在需要时添加。
- library crate 不应把 `color-eyre` 作为公共错误类型。

## 后端服务或复杂应用

```text
src/
├── domain/
├── application/
├── ports/
├── adapters/
│   ├── http/
│   ├── cli/
│   ├── db/
│   ├── storage/
│   └── external/
├── config.rs
├── error.rs
└── main.rs
```

- `main.rs` 负责组装 adapters、application 和配置。
- HTTP handler、CLI 命令、数据库实现、存储实现、第三方服务接入都放在 `adapters` 下。
- `application` 通过 `ports` 依赖外部能力，不直接依赖具体实现。
- `adapters` 子目录只在确实使用对应能力时创建。

## 拆分后的 Workspace 示例

```text
crates/
├── server/
│   └── src/
│       ├── domain/
│       ├── application/
│       ├── ports/
│       ├── adapters/
│       │   ├── http/
│       │   ├── cli/
│       │   ├── db/
│       │   ├── storage/
│       │   └── external/
│       ├── config.rs
│       ├── error.rs
│       └── main.rs
├── third-party-client/
│   └── src/
│       ├── lib.rs
│       ├── client.rs
│       ├── config.rs
│       ├── error.rs
│       ├── types.rs
│       └── signing.rs
└── object-storage/
    └── src/
        ├── lib.rs
        ├── client.rs
        ├── config.rs
        ├── error.rs
        └── types.rs
```

- `third-party-client` 只负责第三方平台 API、签名、请求响应类型和底层错误。
- 主 crate 的 `adapters/external` 负责把 `third-party-client` 适配成 `ports` 中定义的边界 trait。
- `object-storage` 只负责文件系统或对象存储的上传、下载、删除、配置和底层错误。
- 主 crate 的 `adapters/storage` 负责把 `object-storage` 适配成 `ports` 中定义的存储 trait。

## 同时提供 CLI 和 Library 的独立 Crate

```text
src/
├── main.rs
├── lib.rs
├── cli.rs
├── commands/
├── core/
├── adapters/
└── error.rs
```

- `main.rs` 是 CLI 入口，安装 `color-eyre`、解析 `clap` 参数并调用库逻辑。
- `lib.rs` 是库入口，暴露可复用能力。
- `cli.rs` 和 `commands/` 只服务 CLI。
- `core/` 放可复用核心逻辑。
- `adapters/` 放该 crate 自己需要的 IO 实现。
