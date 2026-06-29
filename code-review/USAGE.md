# code-review 使用示例

## 安装

如果你已经拿到打包产物：

- `/Users/bytedance/workspace/skill/dist/code-review.skill`

可以把这个 `.skill` 文件作为可迁移产物保存或导入到你的 skill 环境中。

如果你当前就是在本地工作区里开发和使用它，可以直接使用目录版：

- `/Users/bytedance/workspace/skill/code-review`

## 触发方式

### 显式触发

先输入：

```text
/code-review
```

再描述你想审查的当前改动。

### 自动触发式提问

如果你的请求已经明确是“审查当前 diff / 当前未提交改动”，也可以直接这么说：

```text
帮我看下当前未提交改动有没有字段传播遗漏
review 一下这次 staged changes，重点看状态分支有没有漏改
检查一下这个本地 diff，有没有 hook 依赖没跟上
```

## 示例 1：新增字段遗漏

```text
/code-review
帮我审查一下当前未提交改动，重点看这次新增的 valid 字段有没有在初始化、mapper、serializer 和测试辅助对象里漏改。
```

预期结果：

- agent 先读取 staged / unstaged diff
- agent 加载 `common-checklist` 和 `typescript-javascript`
- agent 输出高置信问题或待人工确认项
- agent 在目标仓库里生成 `code-review-docs/`

## 示例 2：React hooks 风险

```text
review 一下这次前端改动，重点看 useEffect/useCallback 依赖和表单 state 有没有遗漏处理。
```

预期结果：

- agent 会自动进入 diff-centered review
- 加载 `common-checklist` 和 `react-hooks`
- 报告里会区分高置信问题与低置信风险

## 示例 3：Node 服务路径漂移

```text
/code-review
检查一下当前服务端改动，有没有 create/update/retry/job/audit 这些路径处理不一致的问题。
```

预期结果：

- agent 加载 `common-checklist` 和 `node-service`
- 优先检查 service、job、queue、client、audit、metrics 一致性
- 不会顺手改代码

## 生成结果示意

```text
your-project/
  code-review-docs/
    current-review.md
    reviews/
      2026-06-22-1530-customer-valid-propagation.md
```

## 结合后续流程

`code-review` 适合放在“代码已经改了，但还没提交”这个阶段。

后续如果你还需要：

- 写代码前先落 spec：接 `code-plan`
- 进入真正实现并强调测试先行：接 TDD
- 根据审查结果继续修复：让 agent 在 review 之后再进入实现步骤
