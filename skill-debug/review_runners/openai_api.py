from __future__ import annotations

import hashlib
import json
import os
from typing import Any
from urllib import request


def run(*, prompt: str, profile: dict[str, Any]) -> str:
    transport = str(profile.get("transport", "http"))
    if transport == "mock":
        return _run_mock(prompt=prompt, profile=profile)
    if transport != "http":
        raise ValueError(f"Unsupported transport `{transport}` for openai_api review runner.")

    provider = str(profile.get("provider", "gpt"))
    token = _load_api_key(profile)
    base_url = str(profile.get("base_url", "")).rstrip("/")
    timeout = int(profile.get("timeout_seconds", 60))
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    if provider == "deepseek":
        payload = {
            "model": str(profile.get("model", "deepseek-chat")),
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        if "thinking" in profile:
            payload["thinking"] = profile["thinking"]
        if "reasoning_effort" in profile:
            payload["reasoning_effort"] = profile["reasoning_effort"]
        response = _post_json(
            url=f"{base_url}/chat/completions",
            headers=headers,
            payload=payload,
            timeout=timeout,
        )
        return _extract_deepseek_text(response)

    payload = {
        "model": str(profile.get("model", "gpt-5")),
        "input": prompt,
    }
    if "reasoning_effort" in profile:
        payload["reasoning"] = {"effort": profile["reasoning_effort"]}
    response = _post_json(
        url=f"{base_url}/responses",
        headers=headers,
        payload=payload,
        timeout=timeout,
    )
    return _extract_openai_text(response)


def _run_mock(*, prompt: str, profile: dict[str, Any]) -> str:
    provider = str(profile.get("provider", "gpt"))
    model = str(profile.get("model", "unknown-model"))
    base_url = str(profile.get("base_url", "unknown-base-url"))
    prompt_digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
    return "\n".join(
        [
            "# Review",
            "",
            "## Backend",
            "",
            "- Runner: `openai_api`",
            f"- Provider: `{provider}`",
            f"- Model: `{model}`",
            f"- Base URL: `{base_url}`",
            f"- Prompt Digest: `{prompt_digest}`",
            "",
            "## Findings",
            "",
            f"- Executed deterministic mock review for `{provider}`.",
            "- The prompt bundle was assembled successfully from the target overlay, evaluation guide, and debug artifacts.",
            "- Review output is suitable for local testing until live credentials are configured.",
            "",
            "## Next Steps",
            "",
            "- Replace the mock transport with real URL/token settings in `skill-debug/runtime/config/backends.local.yaml` when ready.",
        ]
    )


def _load_api_key(profile: dict[str, Any]) -> str:
    if "api_key" in profile and str(profile["api_key"]).strip():
        return str(profile["api_key"])
    env_name = str(profile.get("api_key_env", "")).strip()
    if not env_name:
        raise ValueError("Review backend profile must define `api_key` or `api_key_env` for HTTP transport.")
    value = os.environ.get(env_name, "").strip()
    if not value:
        raise ValueError(f"Environment variable `{env_name}` is required for the review backend.")
    return value


def _post_json(*, url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url=url, data=data, headers=headers, method="POST")
    with request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def _extract_openai_text(response: dict[str, Any]) -> str:
    output_text = response.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    output = response.get("output", [])
    for item in output:
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            if isinstance(content.get("text"), str) and content["text"].strip():
                return content["text"].strip()
    raise ValueError("OpenAI Responses API reply did not contain text output.")


def _extract_deepseek_text(response: dict[str, Any]) -> str:
    for choice in response.get("choices", []):
        if not isinstance(choice, dict):
            continue
        message = choice.get("message", {})
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
    raise ValueError("DeepSeek chat completion reply did not contain message content.")
