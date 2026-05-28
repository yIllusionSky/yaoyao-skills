---
name: rust-architecture
description: Rust 项目架构规范技能。用于设计、创建或调整 Rust CLI、小工具、library crate、后端服务、复杂应用、workspace crate 拆分、domain/application/ports/adapters 四层边界、错误处理和测试结构。
---

# Rust Architecture

用于规划和维护 Rust 项目结构。除固定技术词外，使用中文说明；按项目复杂度选择最小够用的结构，不为模板完整性创建空目录。

需要具体目录树示例时，读取 [layouts](./references/layouts.md)。

## 架构概念

复杂应用只使用四个核心概念：`domain`、`application`、`ports`、`adapters`。

- `domain`：纯业务核心，放实体、值对象、业务规则、状态流转、领域事件和纯校验逻辑。不得依赖外部框架、数据库、网络、文件系统、CLI、HTTP 或第三方 SDK。
- `application`：用例和流程编排，放应用服务、命令/查询对象、事务边界、权限/上下文检查、跨能力编排。可以依赖 `domain` 和 `ports`，不得直接依赖具体外部实现。顶层目录使用 `application`，不要用 `services` 或 `system` 作为层名；确实需要 service 组织形式时，放在 `application` 内部模块。
- `ports`：`application` 需要的边界 trait，只为外部能力建立接口，例如数据库访问、对象存储、第三方服务、通知发送、时间、ID 生成、事务管理等。不要为普通 helper、纯内部函数或没有边界意义的逻辑建立 trait。
- `adapters`：外部世界的接入和实现。进入系统的 adapter 包括 HTTP 和 CLI；系统调用外部的 adapter 包括数据库、文件系统/对象存储、第三方服务等。`adapters` 负责实现 `ports`、转换外部类型、做错误映射和完成具体 IO。

## Adapter 目录

只在项目确实使用对应能力时创建 adapter 目录，不创建空目录。

- `adapters/http`：HTTP 入口 adapter。
- `adapters/cli`：CLI 入口 adapter，所有 CLI 使用 `clap`。
- `adapters/db`：数据库 adapter。
- `adapters/storage`：文件系统或对象存储 adapter。
- `adapters/external`：第三方服务 adapter。

## 结构选择

- 简单 CLI 或小工具：优先使用 `main.rs`、`cli.rs`、`core.rs`、`error.rs`。`main.rs` 只安装 `color-eyre`、解析 CLI、调用 `core` 入口；`cli.rs` 使用 `clap`；`core.rs` 放核心执行逻辑和纯业务逻辑；`error.rs` 使用 `thiserror`。不需要 `lib.rs`，除非同时要作为 library 复用。
- 稍复杂 CLI 或小工具：使用 `main.rs`、`cli.rs`、`commands/`、`core/`、`adapters/`、`error.rs`。`commands/` 放不同命令入口，`adapters/` 放文件系统、网络、时间、外部命令等 IO 实现。
- 普通 library crate：使用 `lib.rs`、`error.rs`、`types.rs`，按需添加 `config.rs`、`client.rs`。`lib.rs` 控制 public API，不塞大量实现。library crate 不把 `color-eyre` 作为公共错误类型。
- 后端服务或复杂应用：使用 `domain/`、`application/`、`ports/`、`adapters/`、`config.rs`、`error.rs`、`main.rs`。`main.rs` 负责组装 adapters、application 和配置。

## Crate 拆分

当 `adapters` 中某些能力边界稳定、通用、可独立测试、依赖隔离价值高、未来可能复用时，可以提取成独立 crate。

- 适合拆分的能力包括第三方 API client、对象存储 client、通知 client、签名/验签、文件导入导出、验证码、proc macro 等。
- 拆出去的 crate 不依赖主 crate，不知道主业务流程。主 crate 通过 `adapters` 把它接回 `ports` 中定义的边界 trait。
- 普通 capability crate 不套完整四层架构，保持 `lib.rs`、`client.rs`、`config.rs`、`error.rs`、`types.rs` 等清晰边界；需要签名就加 `signing.rs`，需要 provider 分发就加 `provider.rs`。
- 如果独立 crate 本身需要 CLI 功能，使用 `main.rs` + `lib.rs` 结构：CLI 入口安装 `color-eyre`、解析 `clap` 参数并调用库逻辑，`lib.rs` 暴露可复用能力。

## 错误处理

- 每个 crate 都要有自己的错误管理，优先使用 `thiserror` 定义结构化错误。
- `color-eyre` 只用于应用入口、CLI、server startup 和顶层错误报告，不作为 library crate 的公共错误类型。
- HTTP adapter 需要把内部错误映射成统一响应格式：

```json
{
  "code": "xxx",
  "msg": "xxx",
  "data": null
}
```

内部错误不直接暴露给客户端；映射为稳定错误码和通用消息，并在服务端记录详细错误。

## 测试规则

- 单元测试优先写在当前模块所在文件内，验证单个函数、模块、`domain` 规则、`application` 分支、错误路径和 adapter 映射逻辑。
- 存在 trait 边界时可用 `mockall`；`mockall` 属性加在 `ports` 的 trait 上，例如 `#[cfg_attr(test, mockall::automock)]`。不要手写 `mock_xxx.rs` 放到 `ports` 里。
- 集成测试写在 `tests/` 目录下，每个文件对应一个明确业务流程、公开 API 或主要能力，文件名表达业务含义，例如 `order_flow.rs`、`callback_flow.rs`、`parser_roundtrip.rs`、`cli_check.rs`、`client_request.rs`。
- 集成测试用于验证公开 API、模块协作、真实 adapter 或近真实环境。数据库、文件系统等关键依赖尽量使用真实或临时隔离环境；第三方服务使用 sandbox、mock server 或本地 fake service，不打生产环境。
- 测试函数在有多步 fallible 操作时优先返回 `Result`；简单断言测试可以直接使用 `assert`。
- 只写有效测试，不写只验证 mock 配置、getter/setter 或框架默认行为的低价值测试。
