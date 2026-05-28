---
name: project-docs
description: 项目文档规范技能。用于创建、审查或维护长期项目文档，包括根 README、子项目 README、根目录 ARCHITECTURE.md、docs/features.md 和 docs/operations.md；适用于项目说明、功能说明、架构说明、运行维护说明和多子项目文档整理。
---

# Project Docs

用于维护长期有效、需要随代码更新的项目文档。除固定技术词、文件名、命令和代码符号外，使用中文；先读取代码、配置、目录结构和现有文档，再写或改文档。

只描述当前真实状态，不编造未实现能力。不处理 issue、PR、changelog、commit、API 文档、临时设计文档或架构决策记录。

## 文档结构

固定文档职责：

```text
README.md
ARCHITECTURE.md
docs/
  features.md
  operations.md
<子项目>/README.md
```

- `README.md`：根目录必须有，作为项目入口。
- `ARCHITECTURE.md`：固定放根目录；项目进入多模块、多 crate、多服务、复杂流程或存在重要依赖边界时创建和维护。
- `docs/features.md`：项目有多个长期功能、业务规则或用户可见能力时创建和维护。
- `docs/operations.md`：项目存在配置、部署、发布、运行、日志、排障或长期服务维护需求时创建和维护。
- `<子项目>/README.md`：每个独立子项目、crate、package、service、app 都要有自己的 README。

不要创建 API 文档、临时设计文档、issue 本地副本或 ADR。不要把所有文档强制放进 `docs/`。

## README

根 `README.md` 写项目入口信息：

- 项目是什么、面向谁、解决什么问题。
- 当前核心能力摘要。
- 安装、运行、测试和常用命令。
- 项目结构概览。
- 指向 `ARCHITECTURE.md`、`docs/features.md`、`docs/operations.md` 的链接；只链接实际存在的文档。

根 README 不写完整架构细节，不堆长期功能规则，不重复其他文档的大段内容。

## 子项目 README

子项目 README 写该子项目自身信息：

- 职责和适用场景。
- 在整体项目中的位置。
- 主要入口、公开能力或命令。
- 依赖哪些内部模块，不应该依赖什么。
- 单独运行、测试或使用方式。

内容可以很短，但必须帮助读者和 AI 判断边界。不要把根项目说明复制到每个子项目 README。

## 架构文档

`ARCHITECTURE.md` 写系统结构和约束：

- 项目概览。
- 总体架构。
- 模块边界。
- 依赖方向。
- 核心流程。
- 数据流。
- 外部依赖。
- 错误处理。
- 测试策略。
- 架构约束。

架构图写在 `ARCHITECTURE.md` 中，统一使用 `mermaid`。根据内容选择合适图类型。图下方用文字解释边界、依赖方向和关键约束。

## 功能文档

`docs/features.md` 写长期功能说明：

- 功能列表。
- 用户入口。
- 核心行为。
- 关键规则。
- 功能之间的关系。
- 明确不支持的能力。

只写已经存在或稳定承诺的长期功能。不写 roadmap、分支计划、issue 分析或一次性实现方案。

## 运行维护文档

`docs/operations.md` 写运行和维护信息：

- 环境变量。
- 配置文件。
- 本地启动。
- 构建和发布。
- 部署步骤。
- 日志和排障。
- 迁移、备份或恢复注意事项。

普通 library 或不需要长期运行维护的项目不强制创建 `docs/operations.md`。

## 更新规则

- 小修小改不强制更新文档。
- 当项目入口、目录结构、子项目职责、功能行为、架构边界、运行方式或配置发生变化时，更新对应文档。
- 删除过期内容；不要保留与代码不一致的历史描述。
- 文档之间避免重复维护同一信息：README 放入口摘要，features 放功能行为，ARCHITECTURE 放结构边界，operations 放运行维护。
