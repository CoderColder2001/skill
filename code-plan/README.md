# code-plan

`code-plan` 是一个显式触发的编码前规划 skill。

它的目标很简单：在真正开始改代码前，先把这次实现要改什么、为什么这样改、会影响哪些模块、是否需要新模块，落成一份简洁但有工程约束力的 spec。

## 什么时候用

在你准备让 agent 开始“写代码 / 改代码 / 修 bug / 加功能”之前，先显式输入：

```text
/code-plan
```

这个 skill 不会对普通编码请求自动触发。默认情况下，只有你明确进入 `/code-plan` 模式后，它才会把“先写 spec，再实现”作为当前线程里的前置门槛。

还有一个受限入口：如果你已经在 `/debug-review` 里完成了 bug 分析，并且明确同意进入**修改方案设计**，当前线程也可以从 `debug-review` 显式 handoff 到 `code-plan`。

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
- 已经通过 `/debug-review` 沉淀了一份 bug 分析文档，现在想基于这份分析进入修改方案设计

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

如果你是从 `/debug-review` 进入：

1. 你先完成一轮 bug 分析并确认最新结论
2. 你明确说“按这份分析进入 code-plan”或“可以开始做修改方案设计了”
3. agent 先读取最新的 `debug-review-docs/current-review.md`
4. 再基于这份分析文档生成 `code-plan-docs/`

## 可复制安装说明

下面这段文字可以直接发给别人：

```text
我这边整理了一个叫 code-plan 的 skill，适合在真正开始改代码前，先让 agent 产出一份轻量实现 spec。

如果你拿到的是打包文件：
/Users/bytedance/workspace/skill/dist/code-plan.skill

把这个 .skill 文件导入到你的 skill 环境里即可。

如果你拿到的是目录版：
/Users/bytedance/workspace/skill/code-plan

把整个 code-plan 目录放进你的本地 skills 目录里即可。

使用时，先显式输入：
/code-plan

然后再描述你的编码任务。它会先在目标项目里生成：
code-plan-docs/current-spec.md
code-plan-docs/specs/YYYY-MM-DD-<topic>.md

确认 spec 后，再进入真正实现。

如果你已经先用 /debug-review 写好了 bug 分析，也可以在确认分析后明确说：
按这份分析进入 code-plan

这时 agent 会把最新的：
debug-review-docs/current-review.md
debug-review-docs/reviews/YYYY-MM-DD-HHmm-<topic>.md

作为修改方案设计的上游上下文。
```

如果你希望看更完整的使用方式，可以直接看同目录下的 `USAGE.md`。
