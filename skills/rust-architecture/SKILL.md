---
name: rust-architecture
description: Rust 项目架构技能。用于规划、创建、审查或重构 Rust CLI、library、后端服务、Cargo workspace，以及按业务组织的 TypeScript + Rust monorepo；普通局部实现修改且不涉及架构边界时不要自动扩展为整体重构。
---

# Rust Architecture

用于维护最小够用、边界清晰且能随业务增长的 Rust 结构。除固定技术词外使用中文说明；先服从项目已有的合理约定，不为模板完整性创建空目录，也不借架构调整修改任务范围外的代码。

## 工作方式

1. 先读取 workspace、根清单、锁文件、入口、现有模块、公开 API、测试和项目规范，判断当前任务是局部实现、模块调整、crate 拆分、monorepo 边界调整还是新项目设计。
2. 找出本次变化所属的业务能力、聚合或用例，以及它允许依赖的方向；不要先按技术名创建目录再寻找内容填入。
3. 选择能完整承载当前需求的最小结构。已有巨型文件时，不为一次局部修改重排无关代码；但不得把新的独立职责继续追加进去，应先抽取本次涉及的能力。
4. 需要选择或调整目录结构时读取 [layouts](./references/layouts.md)。同时存在 TypeScript 与 Rust workspace，或任务涉及 monorepo 边界、共享包、跨语言契约与 CI 时读取 [monorepo](./references/monorepo.md)。后端服务或复杂应用必须读取 [backend design](./references/backend-design.md)。新增或重组测试时读取 [testing](./references/testing.md)。存在 REST HTTP adapter 时读取 [HTTP errors](./references/http-errors.md)。

## 顶层边界

后端服务使用 `domain`、`application`、`ports`、`adapters` 表达四类顶层依赖边界，而不是四个单文件或四个万能模块。每层继续按真实业务能力、聚合或用例拆分；具体职责和依赖规则见 [backend design](./references/backend-design.md)。

- `domain`：业务状态、规则、不变量和领域错误。
- `application`：用例、授权、事务意图和跨能力编排。
- `ports`：由核心调用方需要定义的外部能力边界。
- `adapters`：HTTP、CLI、数据库、存储和第三方系统等具体接入或实现。
- `main.rs` 是 composition root，只初始化配置、日志和运行时，组装 adapters 与 application，并启动入口。

不得创建代表整个服务的 God repository、God application façade 或全局 `contracts` 类型桶。`mod.rs`、`lib.rs` 和 `main.rs` 默认只放模块声明、受控 re-export、公开 API 或组装代码，不持续堆积业务实现。

## 模块增长

按“内聚函数 → 单文件模块 → 目录模块 → 同 crate 多个业务模块 → capability crate → 独立服务”逐级演进，不因文件变长直接跳到拆 crate，也不机械地一类型一文件。

- 按共同不变量和共同变化原因保持内聚；同时出现多个可独立变化的业务能力、用例组或外部能力时拆分。
- 手写 Rust 文件接近或超过 500 行时必须审查职责、公开项数量和变化原因；超过 800 行时必须拆分，或在架构文档或变更说明中记录其仍保持单一职责的具体理由。
- 自动生成且不手工维护的文件可以超过阈值，但必须能明确识别生成来源，不得把手写逻辑混入生成文件。
- 入口模块只做索引和组装。不要用 crate 级 `allow(clippy::too_many_lines)` 掩盖设计问题；必要例外缩小到具体 item 并说明原因。

## 结构选择

- 简单 CLI 或小工具：使用 `clap`，入口安装 `color-eyre`、解析参数并调用核心入口；业务错误需要调用方匹配时使用 `thiserror`。纯逻辑和 IO 开始独立变化后再拆 `commands`、业务模块和 adapters。
- 普通 library crate：由 `lib.rs` 控制最小 public API，使用 `thiserror` 定义可匹配错误，不把 `color-eyre` 暴露为公共错误；声明支持的 `rust-version`。少量内聚类型可以同文件，增长后按领域命名拆分，避免长期使用泛化 `types.rs`。
- 后端服务或复杂应用：使用四类顶层边界，并在层内按业务能力拆分；`main.rs` 只做组装。需要被集成测试、辅助 binary 或其他 crate 复用时增加 `lib.rs`。
- 同时提供 CLI 和 library：`main.rs` 只负责 `clap`、`color-eyre` 和调用库入口，可复用能力留在 library 模块。
- TypeScript + Rust monorepo：顶层先按业务能力组织可部署应用，再在业务内部选择语言和应用形态；只有真实跨业务复用的 TypeScript package 或 Rust crate 才进入全局共享区。具体布局、workspace、跨语言契约和 CI 规则见 [monorepo](./references/monorepo.md)。

## Crate 与公开 API

- 只有能力边界稳定、依赖隔离或独立测试价值明确、所有权清晰，或构建形态要求独立时才拆 crate；未来可能复用不能单独作为理由。proc macro 必须放在独立 proc-macro crate。
- capability crate 不套完整四层目录，按实际能力使用清晰命名的模块；拆出的 crate 不依赖主业务 crate，也不知道主业务流程。
- 明确 public API，默认保持最小可见性；不要为了测试把内部实现改成 `pub`。修改公开类型、错误、feature 或 MSRV 时检查 SemVer 和下游兼容性。
- feature 优先表达用户可选择的能力或后端。具体实现名确实构成公开选择时可以使用实现型名称，不为隐藏依赖细节制造难懂别名。

## 错误与验证

- `color-eyre` 只用于 binary 入口、CLI、server startup 和顶层错误报告，不作为 library 公共错误，也不替代可匹配的业务错误。
- 外部实现错误在 adapter 边界映射；domain 和 application 不暴露数据库、HTTP 或第三方 SDK 错误类型。
- 本地修改后优先检查涉及 crate：`cargo fmt -p <package> -- --check`、`cargo clippy -p <package> --all-targets -- -D warnings` 和 `cargo test -p <package>`。
- 同时检查本次涉及的 feature 组合。只有项目明确保证所有 feature 可同时启用时才使用 `--all-features`；互斥 feature 使用项目声明的 feature matrix。
- CI 默认验证 workspace 级 fmt、clippy 和 test。成本不可接受时必须有可靠的受影响范围计算，并定期执行全量检查。
