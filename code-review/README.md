# code-review

`code-review` 是一个聚焦于**当前未提交改动**的代码审查 skill。

它的目标不是做泛泛而谈的 code style review，而是优先发现这类问题：

- 新增字段、状态、契约后，影响链没有改完整
- 一个路径改了，另一个平行路径漏改
- React hooks 依赖或闭包上下文漂移
- Node 服务链路里 retry / job / audit / metrics 跟不上本次变更

## 安装

有两种安装方式。

### 方式 1：使用打包产物

如果你希望直接导入可迁移产物，使用：

- `/Users/bytedance/workspace/skill/dist/code-review.skill`

把这个 `.skill` 文件导入到你的本地 skill 环境即可。

### 方式 2：使用目录版

如果你就是在本地工作区里开发或维护它，也可以直接使用目录版：

- `/Users/bytedance/workspace/skill/code-review`

把整个 `code-review` 目录放进你的本地 skills 目录即可。

常见位置通常是：

- `~/.agents/skills/` 适合 Codex
- `~/.claude/skills/` 适合 Claude Code

安装时只需要 `code-review/` 目录或 `.skill` 打包文件本身。像 `code-review-workspace/` 这类评测目录不属于运行时必需内容，不需要一起安装。

## 什么时候用

下面两种情况都适合触发它：

1. 显式输入：

```text
/code-review
```

2. 直接提出明显的 diff 审查请求，例如：

```text
帮我看下当前未提交改动有没有遗漏处理
review 一下这个 diff，重点看新增字段有没有漏改
检查一下这次 staged changes 有没有状态分支没跟上
```

## 默认审查对象

默认审查当前仓库里的：

- staged diff
- unstaged diff

如果当前没有未提交改动，它会明确说出来，而不是硬凑一个审查范围。

## 会产出什么

默认是双轨输出：

1. **对话里给摘要**
2. **在目标仓库里写完整 Markdown 报告**

输出路径默认是：

```text
code-review-docs/
  current-review.md
  reviews/
    YYYY-MM-DD-HHmm-<topic>.md
```

其中：

- `reviews/...md` 是本次完整审查报告
- `current-review.md` 是当前最新一份报告的稳定入口

## 报告长什么样

正式报告固定包含这些部分：

- 审查范围
- 变更摘要
- 本次启用的检查 pack
- 高置信问题
- 疑似风险 / 待人工确认
- 测试与验证缺口
- 建议补充的回归场景
- 未覆盖范围

## v1 的检查方式

`code-review` 采用：

- 一个通用 `common-checklist`
- 多个按需加载的专项 pack

当前首批 pack：

- `typescript-javascript`
- `react-hooks`
- `node-service`

也就是说，它不会上来就把整个仓库翻一遍，而是：

1. 先看 diff
2. 再判断要加载哪些 pack
3. 最后只回看少量相关上下游文件验证是否存在遗漏

## 关于测试检查

这个 skill **不会装懂项目测试体系**。

它只会在仓库里能找到这些证据时，才评论测试同步问题：

- 附近已有测试文件
- fixture / mock / builder / test utility
- 明确的测试命名或测试约定

如果没有相关测试资产，它会直接跳过这部分检查，并明确写出“本次未执行测试同步审查”，而不是空口说“应该补测试”。

## 不负责的事

`code-review` v1 默认**不做这些事**：

- 直接修改生产代码
- 自动修复问题
- 泛化的风格点评
- 与当前 diff 没直接关系的历史坏味道清理
- 无证据支撑的测试建议

它是一个**审查型** skill，不是自动修复器。

## 目录内容

- `SKILL.md`：主契约
- `references/common-checklist.md`：通用传播审查清单
- `references/pack-selection.md`：专项 pack 路由规则
- `references/packs/*.md`：专项审查 pack
- `templates/review-report.md`：正式报告模板
- `templates/current-review.md`：当前报告入口模板
- `evals/evals.json`：轻量评测 prompt

## 典型流程

1. 你输入 `/code-review` 或直接提出 diff 审查请求
2. agent 读取 staged / unstaged diff
3. agent 加载 `common-checklist` 和必要的专项 pack
4. agent 回看少量相关文件验证遗漏
5. agent 在目标仓库里写 `code-review-docs/`
6. 你先看到摘要，再决定是否继续修复
