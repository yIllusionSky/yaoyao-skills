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

- `main.rs`：初始化并调用 `run`，技术选型见主 skill。
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

配置、签名和请求构造独立变化后分别归入对应模块，避免全部追加到 `client.rs`。

## 简单后端服务

```text
src/
├── main.rs
├── http.rs
└── health.rs
```

适合少量健康检查或简单查询接口：`main.rs` 组装并启动，`http.rs` 处理传输，`health.rs` 承载对应能力。出现复杂业务规则或多个外部边界时，再按主 skill 选择依赖结构。

## 已采用四类边界的小型后端

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

`courses`、`questions` 等对应不同能力的 HTTP 和 DB 实现；`shared.rs` 仅在存在明确的底层共享机制时使用。职责、DTO、事务和错误边界遵守 [backend design](./backend-design.md)。

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

`third-party-client` 和 `object-storage` 分别封装稳定的外部能力，主服务通过 adapter 将它们接回 port。是否拆 crate 按主 skill 的判据决定。
