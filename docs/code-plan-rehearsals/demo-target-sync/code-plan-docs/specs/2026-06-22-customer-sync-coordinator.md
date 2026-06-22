# 客户同步协调模块预审 Spec

## 当前编码意图

- 当前任务是在 `demo-target-sync` 项目中，为现有客户同步流程补一个独立的同步协调模块，用来统一承载多外部系统调用的编排、后续重试入口和失败回退扩展点。
- 这次改动想要改变的行为是：不再让 `customer-sync-service.ts` 同时承担“业务入口”和“外部系统协调编排”两层职责，而是把跨系统同步的协调逻辑收口到新模块。
- 这次改动现在需要做，是因为当前同步流程只接了两个 client，但调度顺序、结果聚合和未来的失败处理已经开始堆在单个 service 里。继续往这里加重试、降级或补偿逻辑，会让职责边界继续发胖。

## 预期目标与完成标准

- 新增一个专门负责跨外部系统同步编排的模块，并让现有 service 或 job 通过它完成同步任务。
- `customer-sync-service.ts` 不再直接串联多个 external client 调用，而是把协调职责交给新模块。
- 新模块的接口足够清晰，后续接入重试、部分失败处理或回退策略时，不需要重新拆分现有 job 层。
- 现有同步成功路径行为保持不变，测试仍能验证 CRM 与 Billing 两个系统的同步结果。
- 本次只建立协调层和委托关系，不顺手引入完整重试机制。

## 当前相关模块现状

- `src/services/customer-sync-service.ts` 当前直接依次调用 `pushCustomerRecord()` 和 `pushBillingProfile()`，同时承担了同步编排、结果聚合和业务入口职责。
- `src/jobs/nightly-sync-job.ts` 负责批量遍历客户并调用 `syncCustomer()`。它目前只知道“逐个执行同步”，并不了解外部系统之间的协调细节。
- `src/clients/crm-client.ts` 与 `src/clients/billing-client.ts` 分别封装单个外部系统调用，各自职责目前比较单纯。
- 测试 `tests/sync/customer-sync.test.ts` 验证的是当前直接串联调用的结果，但还没有为“协调层职责独立”建立边界。

## 本次涉及改动模块

- `src/services/customer-sync-service.ts`
  - 变更原因：当前这里同时承担入口和协调职责，是最需要瘦身的位置。
  - 预期职责变化：保留面向上层的业务入口职责，把跨系统同步编排委托给新模块。
- `src/jobs/nightly-sync-job.ts`
  - 变更原因：需要确认 job 仍然只负责任务遍历和调度，不被新模块反向污染。
  - 预期职责变化：原则上不承载新的协调细节，最多只适配新的 service 接口。
- `src/clients/crm-client.ts`
  - 变更原因：作为新协调模块的下游依赖，需要保持 client 的单系统职责边界清晰。
  - 预期职责变化：不接收协调职责，只继续提供单一外部系统调用。
- `src/clients/billing-client.ts`
  - 变更原因：同样会成为新协调模块的下游依赖。
  - 预期职责变化：继续保持 Billing 单系统调用职责，不引入聚合逻辑。
- `tests/sync/customer-sync.test.ts`
  - 变更原因：需要验证 service 到协调模块的委托关系仍然产出原有结果。
  - 预期职责变化：补足对新模块存在后的回归验证，避免只看最终成功结果却忽视边界退化。
- `src/coordinators/customer-sync-coordinator.ts`
  - 变更原因：这是本次新增模块的建议落点，用来承接跨系统同步编排。
  - 预期职责变化：新增文件，负责协调多个 client 调用、统一结果聚合，并为重试/补偿扩展保留接口位置。

## 新模块架构设计陈述

- 需要新模块：是。
- 建议新增模块位置：`src/coordinators/customer-sync-coordinator.ts`
- 新模块职责：
  - 接收单个 `customerId` 的同步请求。
  - 协调 CRM 与 Billing 两个 client 的调用顺序。
  - 聚合跨系统同步结果，向上游返回统一的同步结果对象。
  - 为后续重试、部分失败、回退策略预留单一收口点。
- 新模块不负责的内容：
  - 不负责批量调度或 cron/job 遍历，这仍然属于 `nightly-sync-job.ts`。
  - 不负责单个外部系统的 API 细节，这仍然属于 `crm-client.ts` 与 `billing-client.ts`。
  - 不负责更高层的业务触发条件判断，这仍然由 service 或调用方决定。
- 依赖方向和上下游关系：
  - `nightly-sync-job.ts` 继续调用 `customer-sync-service.ts`
  - `customer-sync-service.ts` 调用 `customer-sync-coordinator.ts`
  - `customer-sync-coordinator.ts` 再依赖 `crm-client.ts` 与 `billing-client.ts`
  - 依赖方向保持从上层业务入口流向协调层，再流向外部系统 client，不反向耦合 job 层
- 公开接口或入口形态：
  - 建议提供单一入口，例如 `coordinateCustomerSync(customerId: string)`
  - 返回统一结果结构，至少包含总体成功状态和各外部系统同步结果
- 为什么新建模块优于继续堆叠在现有模块里：
  - 现在的 `customer-sync-service.ts` 已经开始同时承担入口和协调职责；继续追加重试或回退逻辑会让 service 变成一个难以测试和复用的总包模块。
  - 独立协调模块可以把“跨系统编排”这个明确职责单独隔离出来，让 service 保持薄、client 保持窄、job 保持只做调度。

## 风险与待确认项

- 需要确认当前项目是否接受新增 `src/coordinators/` 目录；如果已有更稳定的组织方式，模块落点应跟随现有惯例。
- 如果后续不止 CRM 和 Billing 两个外部系统，统一结果结构可能需要现在就稍微抽象，否则很快又要改返回类型。
- 测试目前偏结果导向，新增协调层后需要防止测试仍然只盯最终 `ok`，却没约束职责边界重新变胖。

## 不在本次范围内的内容

- 不在这一轮实现完整重试策略。
- 不在这一轮实现失败补偿或回滚编排。
- 不顺手把 job 系统改成并发调度框架。
- 不引入通用工作流引擎或状态机框架。
