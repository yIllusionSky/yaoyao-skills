# Rust Backend Design

用于已根据主 skill 选择四类边界的后端服务和复杂应用。四类是依赖职责，不是固定目录或文件数量；可以作为顶层模块，也可以在按业务能力组织的模块内体现。先确定真实业务能力、聚合或用例，再保持以下依赖方向。

## 依赖方向

```text
inbound adapter ──> application ──> domain
                         │
                         └───────> ports <── outbound adapters

composition root ──> concrete adapters + application wiring
```

- `domain` 不依赖 application、ports 或 adapters。
- `application` 只依赖 domain 和自身需要的 ports。
- inbound adapter 调用 application；outbound adapter 实现 ports。
- composition root 可以看见具体实现，但不承载业务规则。
- 禁止循环依赖，也不要用公共 `utils`、`common` 或全局类型桶绕过边界。

## Domain

一个 domain 模块对应一组共同不变量和共同变化的业务概念，例如一个聚合、值对象族、状态机或规则集合。

- 放实体、值对象、领域规则、状态流转、领域事件、纯校验和领域错误。
- 可以依赖 `std` 和不携带 IO/框架语义的通用值类型库，例如 UUID、时间或 decimal。
- 默认不派生 HTTP、OpenAPI、SQLx、ORM 或第三方 SDK 类型。只有序列化本身就是稳定领域契约且不会绑定传输格式时才在 domain 使用 `serde`。
- 不读取环境变量，不访问数据库、网络、文件系统或时钟，不生成随机 ID；这些能力由 application 通过 ports 提供。
- 同时出现多个可独立演进的不变量集合时拆模块，不建立覆盖全部业务规则的 `domain/mod.rs`。

## Application

application 以用例或内聚用例组组织，不以“整个服务”组织。

- 放 command/query、用例输入输出、授权与上下文检查、事务意图和跨能力编排。
- 简单且共享同一聚合与依赖的 CRUD 可以组成一个 application service；不同角色、资源或流程独立变化时拆分。
- 不创建拥有整个服务全部操作的 `AppService`、`Application` 或 façade。HTTP handler 依赖对应用例组，而不是万能应用对象。
- application 不解析 HTTP、执行 SQL、读取环境变量或依赖具体 SDK；也不把 adapter 错误直接返回给调用方。
- 只有多个 inbound adapter 确实需要稳定且可替换的应用接口时才定义 inbound port；普通用例可直接使用具体 application 类型。

## Ports

port 由调用方需要的外部能力定义，而不是由数据库、SDK 或表结构定义。

- 一个 trait 表达一个内聚 capability 或聚合边界，例如 `CourseRepository`、`QuestionRepository`、`ObjectStorage`、`Clock`。
- 禁止用 `AppRepository`、`SystemRepository` 或全服务名称容纳多组无关操作；出现多组独立方法时拆成小 trait，使同一 adapter type 可以在不同模块分别实现它们。
- 不机械复制每张表的 CRUD，也不为纯 helper、单一内部函数或没有替换边界的逻辑创建 trait。
- 参数和返回值使用 domain/application 类型，不暴露 SQLx transaction、HTTP request、SDK response 或数据库 row。
- 多个 port 需要统一注入时在 composition root 组合依赖，不因注入方便合并接口。

## Adapters

adapter 先按接入类型分组，再按业务能力继续拆分。

- `adapters/http`：route、认证信息提取、请求 DTO、响应 DTO、状态码和错误映射；每个资源或用例组独立模块。
- `adapters/cli`：所有 CLI 使用 `clap`；只做参数解析、输入输出和 application 调用。
- `adapters/db`：实现 repository ports、SQL、row 映射和数据库错误映射；按 capability/聚合拆模块，不建立一个覆盖所有 port 的巨型 impl。
- `adapters/storage`：文件系统或对象存储实现。
- `adapters/external`：第三方 client 的调用和协议转换。
- 跨 adapter 共享的底层机制必须有明确、稳定的共同职责；不要用 `shared.rs`、`common.rs` 或 `utils.rs` 接收暂时无处放置的代码。

## DTO 与 Contracts

- HTTP request/response DTO 默认放在对应 HTTP capability 模块或其相邻 `dto.rs`。
- Utoipa schema/response 派生、HTTP response 实现以及仅服务 HTTP wire format 的 `serde` 属性只放在传输边界类型上，不为生成 OpenAPI 把框架派生扩散到 application 或 domain 类型；domain 使用 `serde` 时继续遵守 Domain 部分的稳定领域契约条件。
- application command/result 放在对应用例模块；domain entity 不直接充当所有 transport DTO。
- 边界 adapter 负责外部类型、application 类型和 domain 类型之间的转换。
- 只有类型被多个入口、crate 或独立消费者共享，并且存在稳定兼容契约时才建立独立 `contracts` 模块或 crate。
- `contracts` 仍按业务能力拆分，禁止把所有请求、响应和内部模型塞进一个全局 `contracts/mod.rs`。

## 事务、配置与错误

- application 决定一个用例需要的原子边界，adapter 负责具体数据库事务。需要跨 repository 原子操作时定义清晰的 unit-of-work/transaction port，或提供与用例对齐的原子 port 方法；不泄漏 SQLx 类型。
- 环境变量和原始配置只在 composition root 或 adapter 侧解析；domain/application 接收经过验证的 typed config 或业务值。
- domain error 表达业务失败，application error 表达用例失败，adapter error 保留外部 source 并在边界映射。不要用一个全局错误枚举收纳所有底层错误。
- REST 错误统一遵守 [HTTP errors](./http-errors.md)。

## 拆分与演进

按以下顺序演进：

```text
内聚函数
→ 单文件模块
→ 目录模块
→ 同 crate 多个业务模块
→ capability crate
→ 独立服务
```

以下任一情况触发拆分审查：

- 一个文件包含多个可独立变化的业务能力、角色流程或外部能力。
- 一个 port trait 出现多组无关方法，或实现必须跨越大量不相关 SQL。
- 一个 application service 被所有 handler 依赖并持续增加无关方法。
- 一个 HTTP 或 DB module 注册、实现多个独立资源组。
- 修改单一能力经常需要在同一批巨型文件中追加代码。
- 手写文件达到主 skill 的 500/800 行审查阈值。

拆分后，每个模块应有清晰名称、最小公开面和单一变化原因；不要用一类型一文件、空层、无行为 DTO wrapper 或无边界 trait 制造形式复杂度。
