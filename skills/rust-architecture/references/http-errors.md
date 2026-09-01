# REST HTTP Errors

用于所有受本规范管理且存在 REST HTTP adapter 的项目。新项目直接采用本契约；已有项目的最终目标也是本契约，但发现不兼容格式时先报告影响，只有当前任务明确包含错误契约迁移时才修改公开响应和客户端。

## 响应契约

所有 HTTP 错误使用统一 envelope：

```json
{
  "error": {
    "code": "PROBLEM_NOT_FOUND",
    "params": {
      "problemId": "123"
    }
  },
  "requestId": "019..."
}
```

- `error.code` 是稳定的 `SCREAMING_SNAKE_CASE` 客户端契约，不复用异常文本。
- `error.params` 始终是 JSON object；没有参数时返回 `{}`。字段使用项目 JSON 命名约定，未定义时使用 `camelCase`。
- `requestId` 是本次请求的 opaque correlation ID，不包含用户信息、错误详情或其他敏感数据。
- 不在 envelope 中增加面向用户的已翻译 `message`；客户端使用 `code + params` 查找本地化模板。

## Request ID

- HTTP 入口为每个请求生成 request ID，或只透传经过校验的可信网关值；未获得可信值时必须生成新值。
- 所有错误响应都返回 `requestId`，包括 `4xx` 和 `5xx`。
- 结构化日志使用同一个 request ID，使客户端报告可以关联入口、数据库和下游调用日志。
- 分布式追踪可以另有 `traceId`；不要把 request ID 当作身份、权限、幂等键或安全 token。

## 状态与错误映射

- 成功使用语义合适的 `2xx`，不套错误 envelope。
- 输入无效、认证、权限、资源不存在、并发或状态冲突等可预期错误使用对应 `4xx` 和稳定业务错误码。
- 未知内部故障统一映射为稳定的内部错误码和 `5xx`，详细 source、数据库错误、堆栈和第三方响应只记录在服务端。
- domain/application 错误在 HTTP adapter 映射为状态码和客户端错误码；不得让 HTTP 类型或状态码进入 domain。
- 同一稳定 `code` 不随内部实现变化改变含义；需要不兼容调整时按公开 API 迁移处理。

## Axum 与 OpenAPI 一致性

- HTTP adapter 的成功响应类型和错误类型同时实现 Axum `IntoResponse` 与 Utoipa `IntoResponses`，使运行时状态、body 和 OpenAPI 描述来自同一组类型；具体规则见 [Axum OpenAPI contracts](./openapi-contracts.md)。
- 错误 body 共用本文件定义的 envelope，但每个 handler 只公开其 operation 完整请求链实际可能返回的错误状态，包括相关 extractor、middleware 和 application 失败；不得用包含全部状态的全局响应集合污染所有 endpoint。
- JSON、path 和 query 提取失败、认证或授权 middleware 拒绝、body 限制、404 fallback 与 405 等框架响应也必须映射为同一错误 envelope，并携带 request ID。
- 契约测试必须确认生成的状态码和 schema 与真实 `IntoResponse` 映射一致，不能只验证 OpenAPI 可以成功序列化。

## 本地化

客户端维护错误码到文案模板的映射，并使用 `params` 插值。语言资源位置服从项目已有 i18n 结构；本规范不强制根 `locales/` 目录。服务端日志应记录可排障上下文，但不得把内部详情复制到客户端参数中。
