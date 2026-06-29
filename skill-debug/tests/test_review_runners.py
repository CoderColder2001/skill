from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest


RUNNER_PATH = Path(__file__).resolve().parents[1] / "review_runners" / "openai_api.py"


def test_openai_http_runner_calls_responses_api(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_openai_runner()
    captured: dict[str, Any] = {}
    monkeypatch.setenv("TEST_OPENAI_KEY", "openai-secret")
    monkeypatch.setattr(
        runner,
        "_post_json",
        lambda *, url, headers, payload, timeout: captured.update(
            {
                "url": url,
                "headers": headers,
                "payload": payload,
                "timeout": timeout,
            }
        )
        or {"output_text": "# Review\n\nOpenAI live response"},
    )

    result = runner.run(
        prompt="Please review this trace.",
        profile={
            "transport": "http",
            "provider": "gpt",
            "base_url": "https://api.openai.example/v1",
            "model": "gpt-5.5",
            "api_key_env": "TEST_OPENAI_KEY",
            "reasoning_effort": "low",
        },
    )

    assert result == "# Review\n\nOpenAI live response"
    assert captured["url"] == "https://api.openai.example/v1/responses"
    assert captured["headers"]["Authorization"] == "Bearer openai-secret"
    assert captured["payload"]["model"] == "gpt-5.5"
    assert captured["payload"]["input"] == "Please review this trace."
    assert captured["payload"]["reasoning"] == {"effort": "low"}
    assert captured["timeout"] == 60


def test_openai_http_runner_calls_deepseek_chat_completions(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_openai_runner()
    captured: dict[str, Any] = {}
    monkeypatch.setenv("TEST_DEEPSEEK_KEY", "deepseek-secret")
    monkeypatch.setattr(
        runner,
        "_post_json",
        lambda *, url, headers, payload, timeout: captured.update(
            {
                "url": url,
                "headers": headers,
                "payload": payload,
                "timeout": timeout,
            }
        )
        or {
            "choices": [
                {
                    "message": {
                        "content": "# Review\n\nDeepSeek live response",
                    }
                }
            ]
        },
    )

    result = runner.run(
        prompt="Please review this trace.",
        profile={
            "transport": "http",
            "provider": "deepseek",
            "base_url": "https://api.deepseek.example",
            "model": "deepseek-v4-pro",
            "api_key_env": "TEST_DEEPSEEK_KEY",
            "thinking": {"type": "enabled"},
            "reasoning_effort": "high",
        },
    )

    assert result == "# Review\n\nDeepSeek live response"
    assert captured["url"] == "https://api.deepseek.example/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer deepseek-secret"
    assert captured["payload"]["model"] == "deepseek-v4-pro"
    assert captured["payload"]["messages"] == [{"role": "user", "content": "Please review this trace."}]
    assert captured["payload"]["thinking"] == {"type": "enabled"}
    assert captured["payload"]["reasoning_effort"] == "high"
    assert captured["payload"]["stream"] is False
    assert captured["timeout"] == 60


def test_openai_http_runner_requires_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_openai_runner()
    monkeypatch.delenv("MISSING_TEST_KEY", raising=False)

    with pytest.raises(ValueError, match="MISSING_TEST_KEY"):
        runner.run(
            prompt="Please review this trace.",
            profile={
                "transport": "http",
                "provider": "gpt",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-5.5",
                "api_key_env": "MISSING_TEST_KEY",
            },
        )


def _load_openai_runner() -> Any:
    spec = importlib.util.spec_from_file_location("test_openai_api_runner", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
