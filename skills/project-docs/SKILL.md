---
name: project-docs
description: 项目文档规范技能。用于创建、审查或维护长期项目文档，包括 monorepo 根 README、子项目 README、根目录 ARCHITECTURE.md、manual-tests.md、docs/features.md 和 docs/operations.md；适用于项目说明、功能说明、手动测试、架构说明、运行维护说明和 monorepo 多子项目文档整理。
---

# Project Docs

用于维护长期有效、需要随代码更新的项目文档。除固定技术词、文件名、命令和代码符号外，使用中文；先读取代码、配置、目录结构和现有文档，再写或改文档。

只描述当前真实状态，不编造未实现能力，不写 roadmap、临时方案、issue 分析或一次性实现计划。不处理 issue、PR、changelog、commit、API 文档、临时设计文档或架构决策记录。

## 文档结构

固定文档职责：

```text
README.md
ARCHITECTURE.md
manual-tests.md
docs/
  features.md
  features/
    <功能域>.md
  operations.md
<子项目>/README.md
<子项目>/manual-tests.md
```

- `README.md`：根目录必须有，作为项目入口。
- `ARCHITECTURE.md`：根目录架构文档；项目存在多模块、多 crate、多服务、复杂流程或重要依赖边界时维护。
- `manual-tests.md`：根项目手动测试文档；记录可直接执行的功能测试命令、前置条件和预期结果。
- `docs/features.md`：长期功能、业务规则和用户可见能力。
- `docs/features/<功能域>.md`：当单个 `features.md` 不足以清晰描述复杂功能域时，按功能域拆分的长期功能文档。
- `docs/operations.md`：配置、部署、运行、日志、排障和维护信息。
- `<子项目>/README.md`：monorepo 中每个独立子项目、crate、package、service、app 都要有自己的 README。
- `<子项目>/manual-tests.md`：可运行子项目的手动测试文档；CLI 写 CLI 命令测试，web / backend 写 `curl` 测试。

## README

根 `README.md` 写项目入口信息：

- 项目是什么、面向谁、解决什么问题。
- 当前核心能力摘要。
- 安装、运行、测试和常用命令。
- 项目结构概览。
- 指向实际存在的长期文档。

根 README 只做入口摘要，不承载完整架构、功能规则、完整手动测试步骤或运维细节。

## 子项目 README

子项目 README 写该子项目自身信息：

- 职责和适用场景。
- 在整体项目中的位置。
- 主要入口、公开能力或命令。
- 依赖哪些内部模块，不应该依赖什么。
- 单独运行、测试或使用方式。

内容可以很短，但必须帮助读者和 AI 判断边界；不要复制根项目说明。

## 架构文档

`ARCHITECTURE.md` 写系统结构和约束，按需覆盖项目概览、模块边界、依赖方向、核心流程、数据流、外部依赖、错误处理、测试策略和架构约束。

架构图写在 `ARCHITECTURE.md` 中，统一使用 `mermaid`。根据内容选择合适图类型。图下方用文字解释边界、依赖方向和关键约束。

## 功能文档

`docs/features.md` 只写已经存在或稳定承诺的长期功能，包括入口、行为、规则、关系和明确不支持的能力。

默认只维护 `docs/features.md`。当功能长期稳定且内容明显过长，或某个功能域需要描述大量规则、状态流转、权限矩阵、配置组合、边界条件、用户可见关系时，可以创建 `docs/features/<功能域>.md`。

拆分后，`docs/features.md` 继续作为功能总览和索引，保留全局规则、跨功能关系和指向功能域文档的链接；功能域文档只写该功能域自身的长期行为和规则。

不要为了临时方案、roadmap、issue 分析、一次性设计、API 参数或内部实现细节创建功能域文档。

## 手动测试文档

`manual-tests.md` 写可直接执行的手动测试，包括前置条件、测试命令、输入和预期结果。

CLI 项目写 CLI 命令测试；web / backend 项目写 `curl` 测试。

根项目存在多个可运行入口时，根 `manual-tests.md` 写全局前置条件和跨子项目测试入口；可运行子项目维护自己的 `manual-tests.md`。

普通 library 或没有稳定可运行入口的项目不强制创建 `manual-tests.md`。

## 运行维护文档

`docs/operations.md` 写长期运行维护信息，包括环境变量、配置、部署、日志排障、迁移、备份和恢复。

普通 library 或不需要长期运行维护的项目不强制创建 `docs/operations.md`。

## 更新规则

- 小修小改不强制更新文档。
- 当项目入口、目录结构、子项目职责、功能行为、架构边界、运行方式、CLI 测试命令、HTTP 测试调用、手动测试步骤或配置发生变化时，更新对应文档。
- 删除过期内容，避免 README、features、ARCHITECTURE、operations 重复维护同一信息。
