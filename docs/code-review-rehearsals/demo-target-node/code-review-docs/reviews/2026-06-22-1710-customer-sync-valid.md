# Customer sync valid 链路一致性审查

## 审查范围

- 审查目标：当前未提交改动
- 是否覆盖 staged diff：否
- 是否覆盖 unstaged diff：是
- 主要查看文件或模块：
  - `src/clients/billing-client.ts`
  - `src/services/customer-sync-service.ts`
  - `src/jobs/nightly-sync-job.ts`
  - `tests/builders/customer-sync-builder.ts`

## 变更摘要

- 这次改动给 billing 同步链路新增了 `valid?: boolean`
- service 到 client 的主路径已经开始传该字段
- 但 nightly job 仍然重新构造旧 payload，只传 `customerId/plan`

## 本次启用的检查 pack

- `common-checklist`
  - 启用原因：这是典型的字段传播和路径一致性问题，需要检查主路径与平行路径是否同步
- `node-service`
  - 启用原因：改动位于 Node service / job 协作链路中，存在 request path 与 background path 漏改风险
- `typescript-javascript`
  - 启用原因：变更同时涉及 DTO 形态和运行时对象构造

## 高置信问题

### 问题 1：nightly job 仍然构造旧 payload，导致 `valid` 在后台路径被丢失

- 变更证据：`src/services/customer-sync-service.ts` 与 `src/clients/billing-client.ts` 已新增 `valid?: boolean` 并在主 service 路径上传递
- 遗漏证据：`src/jobs/nightly-sync-job.ts` 调用 `syncCustomerToBilling` 时重新构造对象，只保留 `customerId` 和 `plan`
- 为什么这是问题：同一个同步链路里，直接 service 调用和 nightly job 调用会对 `valid` 产生不同结果，属于确定性的路径处理不一致
- 建议修复方向：job 路径要么直接透传 `customer`，要么显式补上 `valid`

## 疑似风险 / 待人工确认

### 风险 1：builder 目前没有显式覆盖 `valid` 默认语义

- 触发信号：`tests/builders/customer-sync-builder.ts` 仍然只提供 `customerId/plan`
- 当前不确定点：因为 `...overrides` 仍允许测试显式传 `valid`，它不一定立刻失效，但测试数据默认结构还没有和新字段语义对齐
- 建议人工确认位置：确认同步相关测试是否应该显式覆盖 `valid` 的 true/false 场景

## 测试与验证缺口

- 是否找到相关测试资产：是
- 当前发现的资产：`tests/builders/customer-sync-builder.ts`
- 结论：builder 没有随新字段显式更新，但是否构成 defect 取决于项目对默认测试数据形态的约定，因此先列为低置信风险

## 建议补充的回归场景

- 场景 1：nightly job 处理 `valid: true` 的客户时，传到 `updateBillingCustomer` 的 payload 不应丢失该字段
- 场景 2：主 service 路径和 nightly job 路径对同一输入应生成一致的 billing payload

## 未覆盖范围

- 未检查任何 retry、rollback 或 audit 逻辑，因为当前 demo 中没有这些实现
- 未检查外部 billing 系统对 `valid` 的真实语义约束
