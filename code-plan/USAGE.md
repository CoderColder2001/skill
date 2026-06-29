# code-plan 使用示例

## 安装

如果你已经拿到打包产物：

- `/Users/bytedance/workspace/skill/dist/code-plan.skill`

可以把这个 `.skill` 文件作为可迁移产物保存或导入到你的 skill 环境中。

如果你当前就是在本地工作区里开发和使用它，也可以直接使用目录版：

- `/Users/bytedance/workspace/skill/code-plan`

## 触发方式

先显式输入：

```text
/code-plan
```

然后再给出具体编码任务。

如果你已经先通过 `/debug-review` 完成 bug 分析，也可以在确认分析后明确进入修改方案设计，例如：

```text
/debug-review
这份分析我认可了。按最新的 current-review.md 进入 code-plan，开始做修改方案设计，但先不要改代码。
```

## 示例 1：修 bug

```text
/code-plan
接下来要修复登录接口偶发返回 500 的问题。先不要改代码，先基于当前项目状态写一份 spec，说明这次 bugfix 的编码意图、目标、相关模块现状、会改到哪些模块，以及不在本次范围内的内容。
```

预期结果：

- agent 先读取相关路由、service、repo、测试
- agent 在目标项目里生成 `code-plan-docs/`
- 你先看到 spec 摘要，而不是直接看到代码改动

## 示例 2：新增模块

```text
/code-plan
我准备在当前项目里新增一个独立的同步协调模块，统一处理多个外部 API 的重试和回退。先别实现，先写 spec，明确为什么需要新模块、模块边界、依赖方向、接口形态，以及本次不会顺手做哪些重构。
```

预期结果：

- spec 会明确指出当前哪个旧模块已经承压
- 会给出建议的新模块路径
- 会写清改动后的调用链
- 会说明新模块负责什么、不负责什么

## 示例 3：从 debug-review handoff

```text
/debug-review
最新这份 bug 分析我确认了。按 current-review.md 进入 code-plan，开始做修改方案设计，但不要直接进入实现。
```

预期结果：

- agent 会把 `debug-review-docs/current-review.md` 作为 planning context
- 会参考最新一份 `debug-review-docs/reviews/*.md`
- 生成新的 `code-plan-docs/current-spec.md`
- 不会把这个 handoff 误当成“直接改代码”

## 生成结果示意

```text
your-project/
  code-plan-docs/
    current-spec.md
    specs/
      2026-06-22-login-500-bugfix.md
```

## 结合后续流程

`code-plan` 适合放在实现前。

后续如果你还需要：

- 更细的任务拆解：接 `writing-plans`
- 真正进入编码并强调测试先行：接 TDD
- 代码写完后的评审：接 code review 相关 skill
- 在写 spec 前先做可修订的 bug 分析：先接 `debug-review`
