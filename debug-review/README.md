# debug-review

`debug-review` 是一个显式触发的 bug 分析 skill。

它的目标不是直接修 bug，也不是对当前 diff 做 code review，而是围绕“用户描述的 bug 表现”去追相关模块和链路，把当前最靠谱的原因判断、待确认假设和下一步验证动作沉淀成一份可持续修订的 Markdown 文档。

## 什么时候用

先显式输入：

```text
/debug-review
```

再描述你看到的 bug 表现、复现线索、怀疑点、模块范围或已知环境差异。

这个 skill 不会自动触发。只有你明确进入 `/debug-review` 后，它才会开始写入分析文档并维持这条分析链。

## 会产出什么

默认会把文档写到目标项目里，而不是写回 skill 目录：

```text
debug-review-docs/
  current-review.md
  reviews/
    YYYY-MM-DD-HHmm-<topic>.md
```

其中：

- `reviews/YYYY-MM-DD-HHmm-<topic>.md` 是某一轮分析或修订的完整快照
- `current-review.md` 是当前活跃分析的稳定入口

正式分析文档固定包含这些部分：

- 审查范围
- Bug 表现与输入上下文
- 当前已确认事实
- 相关模块与关键链路
- 高置信原因判断
- 待确认假设与缺失证据
- 建议补充的验证动作
- 用户反馈与修订记录
- 后续入口
- 未覆盖范围

## 适合的场景

- 用户只知道“哪里坏了”，还没有修改方案
- 需要 agent 先审查当前项目里的相关模块和链路，再判断更可能的原因
- 想把分析过程落成一份可回看、可修订、可 handoff 的文档
- 希望先让用户订正或补充分析，再决定是否进入修改方案设计

## 不负责的事

`debug-review` 不是：

- 自动修复 bug 的 skill
- 当前 diff 的传播遗漏审查工具
- 仓库级长期架构文档生成器
- 未经用户确认就自动进入 `code-plan` 的前门

它默认停在 bug 分析阶段。

## 用户如何修订分析

这个 skill 支持两种修订方式：

1. **直接在对话里补充或订正**
   - 补日志
   - 改正环境信息
   - 指出某个推断不成立
   - 追加新的复现线索

2. **直接修改分析文档**
   - 编辑 `debug-review-docs/current-review.md`
   - 或编辑最新一份 `debug-review-docs/reviews/*.md`

agent 会把这些内容当成新的分析输入，而不是无视用户订正。

## 如何进入 `code-plan`

默认情况下，`debug-review` 只停在分析。

当你确认分析已经足够支撑下一步设计时，可以明确说：

```text
按这份分析进入 code-plan
```

或者：

```text
可以开始做修改方案设计了
```

这时最新的：

- `debug-review-docs/current-review.md`
- 最新一份 `debug-review-docs/reviews/YYYY-MM-DD-HHmm-<topic>.md`

会成为 `code-plan` 的上游上下文。

## 目录内容

- `SKILL.md`：skill 主契约
- `templates/review-report.md`：正式分析文档模板
- `templates/current-review.md`：当前活跃分析入口模板
- `references/analysis-checklist.md`：symptom-first 分析清单
- `references/evidence-rules.md`：高置信原因 / 待确认假设分层规则
- `references/handoff-to-code-plan.md`：进入 `code-plan` 的移交流程
- `evals/evals.json`：轻量评测 prompt
- `USAGE.md`：安装与使用示例

## 快速安装

### 目录版：当前工作区直接使用

如果你当前就在本地工作区开发和使用它，可以直接使用目录版：

- `/Users/bytedance/workspace/skill/debug-review`

### 全局安装到 `$CODEX_HOME/skills`

如果你的环境使用 `$CODEX_HOME/skills` 作为全局 skill 目录，可以执行：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R /Users/bytedance/workspace/skill/debug-review "${CODEX_HOME:-$HOME/.codex}/skills/"
```

### 复制到其他工作区

如果你想把这个 skill 快速带到另一个工作区，可以执行：

```bash
mkdir -p /path/to/other-workspace/skills
cp -R /Users/bytedance/workspace/skill/debug-review /path/to/other-workspace/skills/
```

### 打包版 `.skill`

打包产物路径：

- `/Users/bytedance/workspace/skill/dist/debug-review.skill`

拿到这个 `.skill` 文件后，可以把它作为可迁移产物保存或导入到你的 skill 环境中。

## 可复制安装说明

下面这段文字可以直接发给别人：

```text
我这边整理了一个叫 debug-review 的 skill，适合在真正设计修复方案前，先让 agent 基于 bug 表现去审查当前项目的相关模块和链路，并把分析写成可持续修订的 Markdown 文档。

如果你拿到的是目录版：
/Users/bytedance/workspace/skill/debug-review

可以直接放进你的本地 skills 目录里使用。

如果你希望全局安装到 $CODEX_HOME/skills：
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R /Users/bytedance/workspace/skill/debug-review "${CODEX_HOME:-$HOME/.codex}/skills/"

如果你拿到的是打包文件：
/Users/bytedance/workspace/skill/dist/debug-review.skill

把这个 .skill 文件导入到你的 skill 环境里即可。

使用时，先显式输入：
/debug-review

然后描述 bug 表现、复现线索或怀疑点。它会先在目标项目里生成：
debug-review-docs/current-review.md
debug-review-docs/reviews/YYYY-MM-DD-HHmm-<topic>.md

如果你补充了更多信息，或者直接修改了分析文档，它会继续修订这份分析。

只有当你明确同意进入修改方案设计时，它才会把最新的 current-review.md 作为上下文交给 code-plan。
```

如果你希望看更完整的使用方式，可以直接看同目录下的 `USAGE.md`。
