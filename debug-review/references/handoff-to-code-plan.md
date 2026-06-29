# Handoff To Code Plan

`debug-review` 默认停在 bug 分析阶段。只有在用户明确同意进入**修改方案设计**时，才允许切换到 `code-plan`。

## 允许 handoff 的信号

下面这类表达可以视为有效 handoff：

- “按这份分析进入 code-plan”
- “可以开始做修改方案设计了”
- “继续出修复方案，但先别改代码”

如果用户只是说：

- “下一步怎么弄”
- “你觉得呢”
- “是不是该修了”

这类表达还不够明确。先提醒用户：如果要进入 `code-plan`，需要明确同意进入修改方案设计。

## handoff 前必须带上的上下文

进入 `code-plan` 前，至少带上这些内容：

- `debug-review-docs/current-review.md`
- 最新一份 `debug-review-docs/reviews/YYYY-MM-DD-HHmm-<topic>.md`
- 用户最近一次明确确认的补充信息或纠正

## handoff 后的边界

- `code-plan` 负责把“准备怎么改”整理成实现前 spec
- `debug-review` 的高置信原因 / 待确认假设分层应继续保留在 planning context 里
- handoff 不等于开始改代码
- 如果 `current-review.md` 缺失或过时，先补齐分析文档，再进入 `code-plan`
