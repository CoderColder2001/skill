# debug-review 使用示例

## 安装

如果你已经拿到打包产物：

- `/Users/bytedance/workspace/skill/dist/debug-review.skill`

可以把这个 `.skill` 文件作为可迁移产物保存或导入到你的 skill 环境中。

如果你当前就在本地工作区开发和使用它，也可以直接使用目录版：

- `/Users/bytedance/workspace/skill/debug-review`

如果你想安装到全局 skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R /Users/bytedance/workspace/skill/debug-review "${CODEX_HOME:-$HOME/.codex}/skills/"
```

## 触发方式

先显式输入：

```text
/debug-review
```

然后再描述 bug 表现、复现线索、怀疑点或相关模块。

## 示例 1：首轮 bug 分析

```text
/debug-review
登录接口在部分租户下偶发返回 500。先别改代码，帮我基于当前项目状态审查相关路由、service、repo 和配置链路，把最可能的原因写成一份 debug-review-docs 下的分析文档。
```

预期结果：

- agent 先围绕 bug 表现定位相关入口和模块
- agent 区分高置信原因与待确认假设
- agent 在目标项目里生成 `debug-review-docs/`

## 示例 2：用户补充信息后修订分析

```text
/debug-review
我们已经有一版分析了。我刚补充了一个事实：只有开启 billing fallback 的租户会触发这个 500，而且我已经直接改了 current-review.md 里的一段判断。请基于最新文档和这个新线索修订 bug 分析。
```

预期结果：

- agent 会先读取最新 `debug-review-docs/current-review.md`
- 再对照新的用户证据和文档改动
- 写出新的 dated review，并刷新 `current-review.md`

## 示例 3：确认进入修改方案设计

```text
/debug-review
这份分析我认可了。按最新的 current-review.md 进入 code-plan，开始做修改方案设计，但先不要改代码。
```

预期结果：

- agent 不会重新做一轮泛化分析
- 会把 `debug-review-docs/current-review.md` 作为 handoff 上下文
- 进入 `code-plan`，生成新的 `code-plan-docs/current-spec.md`

## 生成结果示意

```text
your-project/
  debug-review-docs/
    current-review.md
    reviews/
      2026-06-23-1530-login-500-fallback.md
```

## 结合后续流程

`debug-review` 适合放在“问题已经出现，但修改方案还没站稳”这个阶段。

后续如果你还需要：

- 基于分析进入修改方案设计：接 `code-plan`
- 已经有 diff，想审查遗漏处理：接 `code-review`
- 做更宽的模块或仓库结构说明：接 `code-analyse`
