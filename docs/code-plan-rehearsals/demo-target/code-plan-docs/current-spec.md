# 当前任务 Spec 入口

- 当前任务标题：登录接口 500 Bugfix
- 最近更新日期：2026-06-22
- 对应 spec：`code-plan-docs/specs/2026-06-22-login-500-bugfix.md`
- 当前状态：`待确认`

## 当前任务摘要

这次任务聚焦在现有登录链路的空值防御和错误映射修复，目标是在不扩张认证系统范围的前提下，让“用户不存在”这类可预期失败不再导致未处理异常和 `500`。

## 当前关注模块

- `src/routes/auth.ts`
- `src/services/auth-service.ts`
- `src/repositories/user-repo.ts`
- `tests/auth/login.test.ts`

## 进入实现前需要确认的点

- 登录失败场景在这个项目里是否应该区分 `4xx` 业务失败和 `5xx` 系统错误。
- `auth-service.ts` 的失败结果是否需要现在就细分类型，还是先做最小收口修复。
