# 当前任务 Spec 入口

- 当前任务标题：客户同步协调模块
- 最近更新日期：2026-06-22
- 对应 spec：`code-plan-docs/specs/2026-06-22-customer-sync-coordinator.md`
- 当前状态：`待确认`

## 当前任务摘要

这次任务聚焦在把跨外部系统的同步编排从 `customer-sync-service.ts` 中拆出来，收口到一个独立协调模块里。目标是为后续重试、部分失败处理和补偿扩展留下稳定边界，同时保持 job、service、client 各自职责清晰。

## 当前关注模块

- `src/services/customer-sync-service.ts`
- `src/jobs/nightly-sync-job.ts`
- `src/clients/crm-client.ts`
- `src/clients/billing-client.ts`
- `tests/sync/customer-sync.test.ts`

## 进入实现前需要确认的点

- 项目里是否接受新增 `src/coordinators/` 这样的目录层级。
- 统一同步结果结构是否需要现在就为未来的部分失败场景预留字段。
