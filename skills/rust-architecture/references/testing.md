# Rust Testing Structure

测试结构跟随业务模块和公开能力，不跟随“所有 repository”“所有 handler”等技术大桶。

## 单元测试

- 小型测试使用当前模块中的 `#[cfg(test)] mod tests`，验证纯函数、domain 不变量、application 分支和 adapter 映射。
- 当测试模块接近或超过 300 行、fixture 明显多于断言，或包含多个独立场景组时，改为 `#[cfg(test)] mod tests;` 和相邻 `tests.rs`；仍保持 unit test，可访问父模块私有项。
- 测试继续按行为分组。不要把生产文件拆小后，又把全部测试集中到层级根 `tests.rs`。
- 有真实 port trait 且交互行为适合 mock 时使用 `mockall`，在 trait 上使用 `#[cfg_attr(test, mockall::automock)]`。不要为了使用 mock 创建没有边界意义的 trait，也不要手写 `mock_xxx.rs` 放进 ports。

## 集成测试

- `tests/` 中每个文件对应一个明确业务流程、公开 API 或 adapter contract，例如 `course_publish_flow.rs`、`question_review_flow.rs`、`parser_roundtrip.rs`。
- 禁止用 `repository_integration.rs`、`http_integration.rs` 等单一技术层文件承载该层所有业务流程；同一 adapter 的不同业务能力应拆开。
- 公共数据库启动、fixture builder、认证 helper 和 fake 放在 `tests/support/`，各测试文件按需 `mod support`；support 不包含具体业务断言。
- 集成测试不依赖 `#[cfg(test)]` 生成的 `Mock*`，因为 crate 作为依赖编译时不会启用这些项。

## Test Double 选择

- mock：验证 application 与 port 的少量交互、分支或错误传播；不要测试 mock 配置本身。
- fake/in-memory adapter：验证多步用例和状态变化，适合稳定且语义可忠实实现的边界。
- mock server：验证第三方 HTTP 协议、状态码、重试和序列化。
- 真实或临时 adapter：数据库、文件系统和关键基础设施使用隔离实例验证事务、约束、查询和映射。
- sandbox：第三方确有官方隔离环境且测试成本可控时使用；绝不调用生产环境。

## Test Support 与质量

- 仅同一 crate 的集成测试共享 helper 时使用 `tests/support/`，不扩大 library public API。
- 只有下游 crate 确实需要复用 fixture、builder 或 fake 时才提供显式 `test-support` feature；默认 feature 不暴露测试工具。
- 多步 fallible 测试可以返回 `Result`，简单断言直接使用标准断言宏。
- 不写只验证 getter/setter、derive、框架默认行为或 mock 是否按配置返回的低价值测试。
- 测试文件和单个测试函数同样接受职责与规模审查；大场景拆成共享 setup 加多个独立行为测试，不用一个数千行函数串联全部流程。
