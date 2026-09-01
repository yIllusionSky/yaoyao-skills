# Axum OpenAPI Contracts

用于新建 Rust REST HTTP 后端，以及从 Rust HTTP adapter 生成跨语言 OpenAPI 契约和 TypeScript 客户端的项目。已有项目先遵守其合理框架与公开契约；只有任务明确包含迁移时才更换框架或响应格式。

## 默认技术栈与边界

- 新建 REST HTTP 后端且没有既有框架约定时默认使用 Axum。
- 需要 OpenAPI 时默认使用 `utoipa` 与 `utoipa-axum`；`utoipa` 必须启用 `axum_extras` 和 `auto_into_responses`，版本由 workspace 统一选择并保持彼此兼容。
- `utoipa-swagger-ui`、Scalar 或其他文档 UI 只在项目需要交互式文档时加入，不是生成契约的必要依赖。
- Axum、Utoipa、HTTP 状态和传输 DTO 只存在于 HTTP adapter；domain 和 application 不依赖这些框架类型。

workspace 依赖应明确保留所需 feature：

```toml
[dependencies]
utoipa = { workspace = true, features = ["axum_extras", "auto_into_responses"] }
utoipa-axum.workspace = true
```

非 workspace 项目使用同样的 feature，并在自身清单中声明相互兼容的版本。

## 路由与契约来源

- 所有需要进入公开契约的 REST handler 使用 `#[utoipa::path]`，并通过 `utoipa_axum::routes!` 注册到 `OpenApiRouter`；不要另外维护一份集中式 path 清单。
- capability router 继续按业务能力拆分，顶层通过 `nest` 或 `merge` 组合。绕过 `OpenApiRouter` 注册的路由默认不进入契约，只允许 health、metrics 等明确不公开的基础设施 endpoint 这样处理。
- 提取一个不连接数据库、不读取运行时秘密且不监听端口的 router 构造函数，使 server 和 OpenAPI exporter 复用完全相同的路由树。
- `operation_id` 一旦被前端、测试或外部消费者使用就视为稳定契约；不得因 Rust 函数重命名无意修改。

## 自动响应与返回类型

`auto_into_responses` 是默认行为。普通 handler 不写重复的 `responses((status = ...), ...)`，而由函数的具体返回类型实现 `IntoResponses`：

```rust
#[utoipa::path(get, path = "/courses/{id}")]
async fn get_course(...) -> Result<OkJson<CourseDto>, GetCourseHttpError> {
    // HTTP adapter 调用 application 并完成类型映射。
}
```

- `Result<T, E>` 的两侧都必须实现 `IntoResponses`；同时分别实现 Axum `IntoResponse`，确保文档与真实响应使用同一类型。
- HTTP adapter 提供少量语义明确的成功类型，例如透明序列化的 `OkJson<T>`、`CreatedJson<T>` 和无 body 的 `NoContent`，分别固定 `200`、`201` 和 `204`。已有等价类型时复用，不为名称一致重复创建 wrapper。
- 错误类型返回 [HTTP errors](./http-errors.md) 定义的统一 envelope，并按 operation 的完整请求链实现 `IntoResponses`：同时覆盖 extractor、认证或授权 middleware、handler 和 application 实际可能产生的状态；状态码声明集中在这些类型上，不散落到每个 handler。
- 需要自动生成契约的普通 handler 不直接返回裸 `Json<T>` 或 `impl IntoResponse`，因为它们不能完整表达可收集的状态集合；使用本地命名 response type 包装。
- 文件下载、流式 body、SSE 或多 content type 等特殊响应由本地命名类型手动实现 `IntoResponse` 与 `IntoResponses`，继续让 handler 返回类型驱动契约。OpenAPI 无法完整表达运行时语义时，使用最接近的 media type/schema 并补充描述，不退回到 handler 上的显式 `responses(...)`。
- 业务资源不存在的 `404` 属于对应 operation 的错误集合；路由不存在的 fallback `404` 和错误 HTTP method 的 `405` 不属于已有 operation，不注入每个 endpoint，但运行时仍使用统一错误 envelope。
- 不建立包含所有 `4xx` 和 `5xx` 的万能 `ApiResponses`；减少标注不能以牺牲 endpoint 契约准确性为代价。

## OpenAPI 导出

- 每个独立部署、独立消费或独立版本化的 API 生成一份 JSON；同一 API 内的业务模块默认组合为一份，不按 Rust 文件数量拆分。
- 服务 crate 暴露纯 OpenAPI/router 构造能力，并提供独立 `export-openapi` binary 或等价仓库命令，将格式稳定的 JSON 写入 `contracts/<api>/openapi.json`。
- exporter 只构造路由和序列化契约，不启动 server，不连接数据库或外部服务，也不依赖生产环境配置。
- server 可以从同一 OpenAPI 对象暴露 `/openapi.json` 或文档 UI，但启动时不得写入仓库。不得使用 `build.rs` 修改受版本控制的 `contracts/`。
- 输出不得包含生成时间、临时端口或环境相关 server URL 等不稳定字段；生成相同源码时必须得到相同内容。

单个服务保留可独立执行的导出入口，根命令只负责枚举和编排，例如：

```text
cargo run -p <api> --bin export-openapi -- --output contracts/<api>/openapi.json
```

## TypeScript 客户端

- `openapi-typescript` 从本地 `openapi.json` 生成 `schema.ts`；生成文件只包含机器生成类型，不混入手写业务逻辑。
- client package 以 `openapi-fetch` 和生成的 `paths` 类型提供薄 client factory；认证、base URL、request ID 和通用错误处理放在手写 middleware 或 factory 中，不重新声明 endpoint DTO。
- 一个独立 API 对应一个 client package。只服务单个业务的 package 留在该业务目录；被多个业务真实复用时才放入根 `packages/<api>-client/`。
- `components["schemas"]` 中的 request/response shape 可以作为 transport DTO 使用，但整个 package 是 API contract/client package，不是 domain model package。
- 提交 OpenAPI JSON 和生成的 TypeScript 类型，并明确标记生成来源与命令；调用方不得手改生成文件。

## 生成与验证

- 根 `contracts:generate` 按“导出全部 OpenAPI JSON → 为每份契约运行 `openapi-typescript`”的顺序更新产物，不改写 client package 中的手写入口。
- 根 `contracts:check` 在临时位置重新生成并与已提交产物比较，或使用工具提供的只检查模式；检查命令本身不得修改工作树。
- Rust 测试至少验证 router 能生成 OpenAPI、关键 path/method/status/schema 存在，以及统一响应类型的 `IntoResponse` 与 `IntoResponses` 保持一致。
- TypeScript 执行 typecheck，并至少用一个成功响应、一个业务错误以及 path/query/body 参数验证 `openapi-fetch` 推导；不使用手写类型断言掩盖契约错误。
- pull request 对 Rust 路由、DTO、错误映射或契约生成配置的修改必须执行 `contracts:check`。具体 workflow 资产由 `github-actions` 技能维护。
