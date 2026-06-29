# Customer valid 字段传播审查

## 审查范围

- 审查目标：当前未提交改动
- 是否覆盖 staged diff：否
- 是否覆盖 unstaged diff：是
- 主要查看文件或模块：
  - `src/models/customer.ts`
  - `src/services/customer-mapper.ts`
  - `tests/builders/customer-builder.ts`

## 变更摘要

- 这次改动在 `CustomerRecord` 和 `CustomerPayload` 上新增了 `valid?: boolean`
- 当前 diff 只修改了类型定义，没有同步修改 mapper、serializer 或测试辅助对象
- 风险集中在“静态类型已经放宽，但运行时对象构造链仍停留在旧结构”

## 本次启用的检查 pack

- `common-checklist`
  - 启用原因：当前改动属于典型字段传播问题，需要检查初始化、mapper、serializer、测试辅助对象是否同步
- `typescript-javascript`
  - 启用原因：变更直接落在 TypeScript 接口与运行时对象构造边界上

## 高置信问题

### 问题 1：`buildCustomerRecord` 没有把新字段传播到运行时对象

- 变更证据：`src/models/customer.ts` 新增了 `CustomerPayload.valid` 和 `CustomerRecord.valid`
- 遗漏证据：`src/services/customer-mapper.ts` 的 `buildCustomerRecord` 仍只返回 `id/email/plan`
- 为什么这是问题：调用方即使传入 `valid`，构造出的 `CustomerRecord` 也会静默丢失该字段，导致类型定义与运行时数据不一致
- 建议修复方向：在 `buildCustomerRecord` 中显式映射 `valid`

### 问题 2：`serializeCustomer` 仍然按旧结构输出 payload

- 变更证据：`CustomerPayload` 已新增 `valid?: boolean`
- 遗漏证据：`src/services/customer-mapper.ts` 的 `serializeCustomer` 返回值没有包含 `valid`
- 为什么这是问题：`CustomerRecord` 上新增的字段无法通过序列化路径向下游传递，容易让上游“以为已经支持”，下游却始终收不到
- 建议修复方向：让 `serializeCustomer` 与最新 payload 结构保持一致

## 疑似风险 / 待人工确认

### 风险 1：builder 当前依赖 `...overrides`，短期可透传，但默认对象语义还未明确

- 触发信号：`tests/builders/customer-builder.ts` 目前通过 `...overrides` 可以传入 `valid`
- 当前不确定点：项目是否希望 builder 对新增字段给出显式默认值，而不是完全依赖覆盖参数
- 建议人工确认位置：确认测试数据里 `valid` 的默认语义是否应该固定为 `false` 或 `undefined`

## 测试与验证缺口

- 是否找到相关测试资产：是
- 当前发现的资产：`tests/builders/customer-builder.ts`
- 结论：没有看到 builder 明确声明新字段默认语义；虽然 `...overrides` 让它暂时不至于完全失效，但围绕 `valid` 的测试数据约束仍然不清晰

## 建议补充的回归场景

- 场景 1：payload 带 `valid: true` 时，`buildCustomerRecord` 产物应保留该值
- 场景 2：record 带 `valid: false` 时，`serializeCustomer` 输出不应丢失该字段

## 未覆盖范围

- 未检查任何真实 API、数据库或缓存路径
- 未检查是否还有其他模块消费 `CustomerPayload`
