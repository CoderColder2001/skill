# 当前审查报告入口

- 当前审查标题：Settings sendDigest 状态同步审查
- 最近更新日期：2026-06-22
- 对应报告：`code-review-docs/reviews/2026-06-22-1705-settings-send-digest.md`
- 当前状态：`已生成`

## 当前审查摘要

这次审查覆盖了 `settings-form.tsx` 新增 `sendDigest` 字段的未提交改动。当前已确认初始化路径和提交路径都没有跟上新增字段的真实 state，是两处高置信问题；由于仓库里没有相关测试资产，本次没有执行测试同步审查。

## 本次重点文件或模块

- `src/components/settings-form.tsx`

## 建议下一步

- 先统一初始化与提交都从同一份 `form` state 读写 `sendDigest`
- 修复后再补一条围绕 checkbox 初始化与提交的回归验证
