# code-study-global

`code-study-global` 是一个显式触发的全局源码架构学习 skill。

它用于基于真实源码证据持续沉淀仓库级架构知识库，适合梳理模块地图、运行时拓扑、依赖边界、启动/请求/事件链路、状态与数据流、外部集成点，以及后续阅读 backlog。有合适案例时，也会提炼项目中值得学习的设计及其解决的问题。

## 什么时候用

显式输入：

```text
/code-study-global
```

或者在请求里明确写 `code-study-global`。

这个 skill 不会因为普通源码问题自动触发，也不会在修改 skill 本身时启动仓库学习。单模块深读使用 `code-study-module`；排障、代码评审和功能实现不属于本 skill 的范围。

## 会产出什么

默认把文档写到目标项目里的 `docs/code-study-global/`：

```text
docs/code-study-global/
  index.md
  current-run.md
  future-work.md
  runs/
  maps/
    module-map.md
    runtime-topology.md
    dependency-boundaries.md
  topics/
    startup-flow.md
    execution-flows.md
    state-and-data-flow.md
    integration-points.md
    design-lessons.md       # 可选：跨模块的设计学习总结
```

`index.md` 是全局入口和索引。`maps/` 存放稳定结构图谱，`topics/` 存放跨模块链路和机制深读。按实际分析范围创建文档，不为了填满目录而生成空文件。每轮学习维护 `current-run.md`、`future-work.md` 和历史 run 记录，具体命令见[运行记录维护](references/run-tracking.md)。

## 值得学习的设计与解决的问题

在相关 map/topic 中按需增加这一节；多个案例跨越模块或需要集中解释时，写入 `topics/design-lessons.md`，并从索引和相关文档链接过去。每个案例说明：

- **问题与约束**：项目中实际要解决什么问题，缺少该机制会有什么影响。
- **设计与实现**：职责、接口、数据结构或协作流程如何解决问题，附源码路径、符号和行号。
- **收益与依据**：哪些效果能从代码或测试、数据中证实，哪些只是明确标注的推断。
- **代价与适用边界**：引入什么成本，何时值得借鉴，何时不适合照搬。

不凑固定数量，不凭模式名称推断设计价值，不虚构作者动机或性能收益。当前阅读范围没有合适案例时，省略该章节和独立文件。

## 设计重点

- 只做全局架构学习，不创建模块 scoped 文档树。
- 根据用户指定的重点和用途展开；未指定时先梳理全局地图和一条代表性链路，不强制追问偏好。
- 保留结构化、渐进式分析和沉淀能力。
- 维护文档边界、返回索引和相关链接；有实际阅读顺序时补充 previous/next 跳转。
- 逻辑、链路、运行时说明需要贴近源码位置引用。
- 每个 `index.md`、`maps/` 和 `topics/` 文档都需要 `Document Snapshot`，记录 project root、branch、HEAD、HEAD 时间与 subject、文档更新时间、源码链接风格，以及 `docs/code-study-global/` 是否被 git 忽略。
- 通过 `index.md` 的 coverage matrix 表达哪些区域已验证、部分覆盖、未开始或可能过期。
- 增量更新时比较相关源码与契约的变化，不因 HEAD 变化就把所有文档判为过期。
- 运行记录工具只依赖 Python 标准库；先读取已有记录再启动新一轮，合并已有 backlog 后再同步。

## 安装

推荐直接使用本目录的安装脚本。脚本会把当前 `code-study-global/` 目录安装到目标 skills 目录，默认使用复制模式；如果你希望开发时联动本目录改动，可以加 `--mode symlink`。

### Trae 全局安装

```bash
./install.sh --client trae --scope global
```

### Trae 工作区安装

```bash
./install.sh --client trae --scope workspace --workspace /path/to/project
```

默认安装到 `/path/to/project/.trae/skills/code-study-global`。

### Codex 全局安装

```bash
./install.sh --client codex --scope global
```

默认目标目录优先使用 `$CODEX_SKILLS_DIR`，其次使用 `$CODEX_HOME/skills`，否则使用 `~/.codex/skills`。如果你的 Codex/Agents 环境仍使用 `~/.agents/skills`，可以显式指定：

```bash
./install.sh --client codex --scope global --dest "$HOME/.agents/skills"
```

### Codex 工作区安装

```bash
./install.sh --client codex --scope workspace --workspace /path/to/project
```

默认安装到 `/path/to/project/.codex/skills/code-study-global`。

### 覆盖安装与自定义目录

目标目录已存在时，脚本默认拒绝覆盖。确认要替换时使用：

```bash
./install.sh --client codex --scope global --force
```

也可以绕过内置路径规则，直接指定任意 skills 目录：

```bash
./install.sh --dest /path/to/skills --force
```

## 目录内容

- `SKILL.md`：skill 主契约
- `references/run-tracking.md`：运行记录命令、路径规则和增量维护说明
- `scripts/code_study_global_run_tracking.py`：运行记录维护脚本
- `templates/`：运行记录和后续工作模板
- `src/`：辅助工具代码
- `tests/`：契约与工具测试
- `install.sh`：安装到 Trae/Codex 的全局或工作区 skills 目录
