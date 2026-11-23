# Code Study Skills

维护仓库级架构学习和单模块源码学习两个技能。

| 技能 | 用途 | 配套内容 |
| --- | --- | --- |
| [code-study-global](code-study-global/SKILL.md) | 持续维护仓库级架构知识库，默认输出到 `docs/code-study-global/` | 运行记录脚本、模板、测试、安装脚本 |
| [code-study-module](code-study-module/SKILL.md) | 围绕指定模块或链路生成有源码引用的学习文档 | 状态溯源参考、行为评估用例和源码样例 |

两个技能均保持显式触发：在请求中指定 `code-study-global` 或 `code-study-module`。

## 安装与维护

将对应技能的整个目录安装到客户端的 skills 目录，保留其中的参考文档、脚本和模板。`code-study-global` 的安装方式见其 [README](code-study-global/README.md#安装)。

本仓库作为维护源；修改、验证并提交后，再按需更新本机安装副本。仓库同步不会自动覆盖本机已安装的技能。不要提交缓存、调试运行日志或本地凭据。

## 验证

`code-study-global` 使用 Python 3.11 或更高版本。在隔离环境中安装开发依赖并运行测试：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e './code-study-global[dev]'
.venv/bin/python -m pytest code-study-global/tests
```

`skill-debug` 是独立的可选集成，不随本仓库发布。保留其接入配置和集成测试；未安装 `skill_debug_tools` 时，该集成测试会跳过，全局学习和运行记录功能可以独立使用。

`code-study-module` 的行为评估方法见 [evals/RUNNING.md](code-study-module/evals/RUNNING.md)。校验 JSON 和样例路径不能替代实际行为评估。
