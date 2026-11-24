# 运行记录维护

运行记录用于衔接多轮源码学习。每轮只记录目标、关键发现、文档变化、未解问题和后续阅读方向。

先阅读目标项目已有的 `index.md`、`current-run.md`、`future-work.md` 和相关 maps/topics，再开始新一轮。`start` 会覆盖当前记录；每轮选择未使用过的 run ID，避免覆盖历史记录。

下面的路径是占位符，执行前替换为实际绝对路径：

- `<skill-root>`：当前 `SKILL.md` 所在目录。
- `<output-root>`：用户指定的文档目录，默认 `<project-root>/docs/code-study-global`。
- `<run-id>`：例如 `csg-YYYYMMDD-HHMMSS-global` 或 `csg-YYYYMMDD-HHMMSS-startup`，使用当前日期时间。

脚本只依赖 Python 标准库，可从目标项目目录执行，无需安装 Python 包。

## 开始一轮

```bash
python3 "<skill-root>/scripts/code_study_global_run_tracking.py" start \
  --output-root "<output-root>" --run-id "<run-id>" \
  --objective "梳理仓库架构与核心启动链路" --status in_progress \
  --focus-topic "模块边界" --focus-topic "启动链路"
```

脚本生成记录骨架，已有 `index.md` 和 `future-work.md` 会保留。补充本轮实际用途、深度、未解问题和源代码基线；将说明文字按主 skill 的语言规则整理。脚本不会自动收集基线、推导架构或验证源码。

## 记录重要进展

```bash
python3 "<skill-root>/scripts/code_study_global_run_tracking.py" append-event \
  --output-root "<output-root>" --run-id "<run-id>" \
  --phase architecture_mapping --action "已梳理模块职责与启动入口" \
  --evidence "实际检查的源码路径、符号与结论" \
  --output "<output-root>/maps/module-map.md" \
  --next-step "追踪入口到主要执行链路的职责交接"
```

`--evidence`、`--output` 可重复。脚本替换 `current-run.md` 中的 Latest Event、Current Output Files 和 Next Immediate Action；历史记录追加本次事件。参数使用真实发现和实际文件，不照抄示例结论。没有实质进展时不必追加事件。

## 同步后续阅读

先合并已有 backlog 与本轮发现，保留仍有效的待办、优先级、原因和完成状态；`sync-future-work` 会替换整个文件，因此传入合并后的完整列表，避免只传新增项而丢失旧内容。

```bash
python3 "<skill-root>/scripts/code_study_global_run_tracking.py" sync-future-work \
  --output-root "<output-root>" \
  --topic "状态流|high|open|主要写入与失效条件尚未追踪|topics/state-and-data-flow.md"
```

`--topic` 可重复，格式为 `topic|priority|status|rationale|suggested_doc`。只有确认不存在待办时才传空列表；若现有 backlog 含脚本无法保留的格式或说明，直接编辑文档。

## 结束一轮

```bash
python3 "<skill-root>/scripts/code_study_global_run_tracking.py" finalize \
  --output-root "<output-root>" --run-id "<run-id>" \
  --status partial --next-topic "状态流"
```

按实际情况设置状态，`--next-topic` 可重复。完成本轮目标不等于完成整个仓库的学习；覆盖范围以 `index.md` 的 coverage matrix 为准。

若 Python 不可用，参考 `templates/current-run.md`、`templates/run.md` 和 `templates/future-work.md` 直接维护记录；按项目编辑规范写入，保留已有内容。运行记录是辅助材料，不应阻断源码阅读和文档交付。
