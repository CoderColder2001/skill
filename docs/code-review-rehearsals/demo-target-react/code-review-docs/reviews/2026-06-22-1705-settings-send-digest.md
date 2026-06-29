# Settings sendDigest 状态同步审查

## 审查范围

- 审查目标：当前未提交改动
- 是否覆盖 staged diff：否
- 是否覆盖 unstaged diff：是
- 主要查看文件或模块：
  - `src/components/settings-form.tsx`

## 变更摘要

- 这次改动给表单状态新增了 `sendDigest: boolean`
- UI 已新增 checkbox，但初始化和提交路径对该字段的处理与表单当前 state 不一致
- 风险集中在“表单展示状态、重置状态和提交 payload 并非同一个数据来源”

## 本次启用的检查 pack

- `common-checklist`
  - 启用原因：需要检查新增字段在初始化、提交和状态同步路径上的传播完整性
- `react-hooks`
  - 启用原因：改动位于 React 组件内部，涉及 `useEffect` 初始化逻辑和 `useCallback` 提交逻辑
- `typescript-javascript`
  - 启用原因：新增字段同时改变了静态类型和运行时对象构造

## 高置信问题

### 问题 1：重置路径把 `sendDigest` 强行写回 `false`，没有沿用 `initialSettings`

- 变更证据：`Settings` 类型新增了 `sendDigest`
- 遗漏证据：`useEffect` 中 `setForm` 只拷贝 `email/timezone`，并把 `sendDigest` 固定写成 `false`
- 为什么这是问题：当外部传入 `initialSettings.sendDigest === true` 时，组件重置后会显示成 `false`，导致 UI 状态与真实初始配置不一致
- 建议修复方向：让初始化逻辑直接采用 `initialSettings.sendDigest`

### 问题 2：提交 payload 使用了 `initialSettings.sendDigest`，而不是当前表单 state

- 变更证据：UI 已允许用户通过 checkbox 修改 `form.sendDigest`
- 遗漏证据：`submit` 中传给 `onSubmit` 的对象使用的是 `initialSettings.sendDigest`
- 为什么这是问题：用户在当前表单里勾选或取消勾选后，提交出去的值仍然是旧初始值，属于确定性的状态漂移
- 建议修复方向：提交时应从 `form.sendDigest` 读取当前值

## 疑似风险 / 待人工确认

### 风险 1：`submit` 的依赖数组当前没有显式包含 `initialSettings`

- 触发信号：`submit` 闭包里读取了 `initialSettings.sendDigest`
- 当前不确定点：当前实现因为依赖数组是 `[form, onSubmit]`，若保留这种读取方式会有 stale closure 风险；如果按建议改为读取 `form.sendDigest`，这个问题会自然消失
- 建议人工确认位置：修复提交逻辑时一并复核 `useCallback` 依赖和闭包读取来源

## 测试与验证缺口

- 是否找到相关测试资产：否
- 如果没找到，明确写：`未发现可依据的相关测试资产，本次未执行测试同步审查`

## 建议补充的回归场景

- 场景 1：当 `initialSettings.sendDigest` 为 `true` 时，组件初始化后 checkbox 应保持选中
- 场景 2：用户切换 checkbox 后提交，`onSubmit` 收到的 `sendDigest` 应与当前表单状态一致

## 未覆盖范围

- 未检查任何父组件、远端保存逻辑或接口层
- 未检查是否存在共享表单 hook 或通用表单 helper
