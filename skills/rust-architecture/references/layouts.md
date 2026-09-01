# Rust 项目布局示例

这些目录树只说明结构如何随职责增长，不是必须创建清单。示例中的 `course`、`question`、`import` 等名称必须替换成项目真实业务概念；没有对应能力时不创建文件或目录。

## 简单 CLI 或小工具

```text
src/
├── main.rs
├── cli.rs
├── run.rs
└── error.rs
```

- `main.rs`：安装 `color-eyre`、解析 `clap` 参数、调用 `run`。
- `cli.rs`：只定义命令和参数。
- `run.rs`：在规模较小时承载单一执行流程和少量内聚逻辑；当命令流程、业务规则或具体 IO 需要独立维护时，将对应职责抽取为命令模块、按业务能力命名的模块或 adapter 模块。
- `error.rs`：需要结构化错误时使用 `thiserror`。

## 增长后的 CLI

```text
src/
├── main.rs
├── cli.rs
├── commands/
│   ├── mod.rs
│   ├── check.rs
│   └── export.rs
├── manifest.rs
├── policy.rs
├── adapters/
│   ├── mod.rs
│   ├── filesystem.rs
│   └── remote.rs
└── error.rs
```

- `commands` 按用户可执行命令组织入口，不承载共享业务规则。
- `manifest`、`policy` 是示意业务能力，共享规则按真实领域命名，不汇总到泛化 `core.rs`。
- `adapters` 只放文件、网络、时间或外部命令等 IO。
- 各 `mod.rs` 只声明模块和受控导出。

## 小型 Library Crate

```text
src/
├── lib.rs
├── client.rs
├── model.rs
└── error.rs
```

- 只创建实际需要的模块；纯模型库不需要 `client.rs`。
- `lib.rs` 控制 public API，不塞实现。
- `model.rs` 只适合少量内聚类型；出现多个独立概念时按领域名称拆分，不长期使用泛化 `types.rs`。

## 增长后的 Library Crate

```text
src/
├── lib.rs
├── client.rs
├── config.rs
├── signing.rs
├── request.rs
├── response.rs
└── error.rs
```

模块按能力或公开概念拆分。不要为了目录对称创建空文件，也不要让 `client.rs` 同时承担配置、签名、协议类型和全部实现。

## 小型后端服务

```text
src/
├── domain.rs
├── application.rs
├── ports.rs
├── adapters.rs
├── adapters/
│   ├── http.rs
│   └── db.rs
├── config.rs
├── error.rs
├── lib.rs
└── main.rs
```

- 仅当每层仍只有一个内聚能力时使用平铺文件。
- `adapters.rs` 只声明实际存在的 adapter。
- `main.rs` 只组装配置、日志、运行时和依赖。
- 任一层出现第二个可独立变化的业务能力时，改用目录模块，不继续扩张单文件。

## 增长后的后端服务

```text
src/
├── domain/
│   ├── mod.rs
│   ├── course.rs
│   ├── knowledge_point.rs
│   ├── question.rs
│   └── review.rs
├── application/
│   ├── mod.rs
│   ├── courses.rs
│   ├── questions.rs
│   ├── imports.rs
│   └── images.rs
├── ports/
│   ├── mod.rs
│   ├── course_repository.rs
│   ├── question_repository.rs
│   ├── import_job_repository.rs
│   └── object_storage.rs
├── adapters/
│   ├── mod.rs
│   ├── http/
│   │   ├── mod.rs
│   │   ├── courses.rs
│   │   ├── questions.rs
│   │   ├── imports.rs
│   │   └── images.rs
│   └── db/
│       ├── mod.rs
│       ├── courses.rs
│       ├── questions.rs
│       ├── imports.rs
│       └── shared.rs
├── config.rs
├── error.rs
├── lib.rs
└── main.rs
```

- 四层是依赖分类；层内文件按业务能力、聚合或用例拆分。
- port 按调用方所需能力命名，不建立覆盖整个服务的 repository trait。
- HTTP route 和 DB 实现都继续按业务能力拆分；`shared.rs` 只放确实跨模块共享的底层机制，不接收无归属逻辑。
- `mod.rs` 只声明模块和受控导出，不承载整层实现。
- DTO、事务和跨层错误放置遵守 [backend design](./backend-design.md)。

## 同时提供 CLI 和 Library

```text
src/
├── main.rs
├── lib.rs
├── cli.rs
├── commands/
│   ├── mod.rs
│   └── export.rs
├── document.rs
└── error.rs
```

- `main.rs` 负责 `clap`、`color-eyre` 和调用 library。
- `commands` 只服务 CLI；可复用能力由 `lib.rs` 暴露。
- library 模块不依赖 CLI 参数类型或顶层报告类型。

## Workspace 与 Capability Crate

```text
crates/
├── server/
│   └── src/
├── third-party-client/
│   └── src/
│       ├── lib.rs
│       ├── client.rs
│       ├── signing.rs
│       ├── model.rs
│       └── error.rs
└── object-storage/
    └── src/
        ├── lib.rs
        ├── client.rs
        ├── config.rs
        └── error.rs
```

- capability crate 只负责自身协议和能力，不知道主业务流程，也不依赖主业务 crate。
- 主服务通过 adapter 把 capability crate 接回对应 port。
- 文件变长本身不足以拆 crate；依赖隔离、所有权、稳定 API、独立测试或构建形态必须至少有一项明确收益。
