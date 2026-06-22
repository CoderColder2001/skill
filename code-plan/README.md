# code-plan

`code-plan` 是一个显式触发的编码前规划 skill。

它的目标很简单：在真正开始改代码前，先把这次实现要改什么、为什么这样改、会影响哪些模块、是否需要新模块，落成一份简洁但有工程约束力的 spec。

## 什么时候用

在你准备让 agent 开始“写代码 / 改代码 / 修 bug / 加功能”之前，先显式输入：

```text
/code-plan
```

这个 skill 不会自动触发。只有你明确进入 `/code-plan` 模式后，它才会把“先写 spec，再实现”作为当前线程里的前置门槛。

## 会产出什么

它会把文档写到被操作项目里，而不是写回 skill 目录：

```text
code-plan-docs/
  current-spec.md
  specs/
    YYYY-MM-DD-<topic>.md
```

其中：

- `specs/YYYY-MM-DD-<topic>.md` 是这次任务的正式 spec
- `current-spec.md` 是当前活跃任务的稳定入口

正式 spec 固定包含这些部分：

- 当前编码意图
- 预期目标与完成标准
- 当前相关模块现状
- 本次涉及改动模块
- 新模块架构设计陈述
- 风险与待确认项
- 不在本次范围内的内容

## 适合的场景

- 修一个范围明确、但不想直接开改的 bug
- 给现有模块加功能，先梳理影响面
- 准备拆分职责或新建模块，需要先把边界说清楚
- 想让 agent 在编码前先做一轮轻量工程审视，而不是直接开始写实现

## 不负责的事

`code-plan` 不是：

- 通用产品设计 skill
- 详细 implementation plan 生成器
- TDD 替代品
- 代码写完后的 review skill

它更像一个 pre-coding gate。spec 通过后，再进入实现、计划细化或后续 review。

## 目录内容

- `SKILL.md`：skill 主契约
- `templates/spec-template.md`：正式 spec 模板
- `templates/current-spec-template.md`：当前任务入口模板
- `examples/spec-example.md`：bugfix 场景示例
- `examples/current-spec-example.md`：`current-spec.md` 示例
- `evals/evals.json`：轻量评测 prompt
- `USAGE.md`：安装与使用示例

## 典型流程

1. 你先输入 `/code-plan`
2. 再提出具体实现请求
3. agent 扫描相关模块、测试、配置和边界
4. agent 在目标项目下写出 `code-plan-docs/`
5. 你确认或修改 spec
6. spec 认可后，才进入真正编码
