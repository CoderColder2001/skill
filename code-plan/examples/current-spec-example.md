# 当前任务 Spec 入口

- 当前任务标题：登录接口 500 Bugfix
- 最近更新日期：2026-06-22
- 对应 spec：`code-plan-docs/specs/2026-06-22-login-500-bugfix.md`
- 当前状态：`待确认`

## 当前任务摘要

这次任务聚焦在现有登录链路的异常处理补强，目标是在不重构认证体系的前提下修复登录接口偶发 `500` 的问题，并补上最小必要的回归测试。

## 当前关注模块

- `src/routes/auth.ts`
- `src/services/auth-service.ts`
- `src/repositories/user-repo.ts`
- `tests/auth/login.test.ts`

## 进入实现前需要确认的点

- 登录失败场景当前对外约定的状态码和错误体是否有兼容性要求。
- `user-repo` 返回空值是否属于设计允许场景，还是底层数据异常。
