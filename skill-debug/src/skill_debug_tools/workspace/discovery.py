from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from skill_debug_tools.common.files import read_yaml

_MANAGED_BLOCK_START = "<!-- skill-debug:managed:start -->"
_MANAGED_BLOCK_END = "<!-- skill-debug:managed:end -->"


class IntegrationState(str, Enum):
    ATTACHABLE = "attachable"
    ATTACHED = "attached"
    BROKEN = "broken"


@dataclass(frozen=True)
class SkillRecord:
    name: str
    root: Path
    skill_path: Path
    state: IntegrationState
    reason: str | None = None


def discover_skills(workspace_root: Path) -> list[SkillRecord]:
    records: list[SkillRecord] = []
    for skill_path in sorted(workspace_root.rglob("SKILL.md")):
        data = _read_skill_frontmatter(skill_path)
        name = str(data.get("name", "")).strip()
        if not name:
            continue
        root = skill_path.parent
        state, reason = classify_skill(root=root, skill_name=name, skill_path=skill_path)
        records.append(SkillRecord(name=name, root=root, skill_path=skill_path, state=state, reason=reason))
    return sorted(records, key=lambda item: (item.name, str(item.root)))


def classify_skill(*, root: Path, skill_name: str, skill_path: Path) -> tuple[IntegrationState, str | None]:
    integration_root = root / "skill-debug"
    config_path = integration_root / "config.yaml"
    guide_path = integration_root / "evaluation-guide.md"
    overlay_path = integration_root / "review-prompt.md"
    state_path = integration_root / "injection-state.json"
    if not config_path.exists():
        return IntegrationState.ATTACHABLE, None
    required = [config_path, guide_path, overlay_path, state_path]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        return IntegrationState.BROKEN, f"missing integration files: {', '.join(missing)}"
    config = read_yaml(config_path)
    if str(config.get("target_skill", "")).strip() != skill_name:
        return IntegrationState.BROKEN, "config target_skill does not match SKILL.md frontmatter name"
    if str(config.get("skill_path", "")).strip() not in {"", "SKILL.md"}:
        return IntegrationState.BROKEN, "config skill_path does not point at SKILL.md"
    state = read_yaml(state_path)
    if str(state.get("target_skill", "")).strip() != skill_name:
        return IntegrationState.BROKEN, "injection-state target_skill does not match SKILL.md frontmatter name"
    if str(state.get("skill_path", "")).strip() not in {"", "SKILL.md"}:
        return IntegrationState.BROKEN, "injection-state skill_path does not point at SKILL.md"
    if str(state.get("managed_block_marker", "")).strip() != "skill-debug":
        return IntegrationState.BROKEN, "injection-state managed_block_marker does not match skill-debug"
    document = skill_path.read_text(encoding="utf-8")
    body = _extract_managed_block_body(document)
    if body is None:
        return IntegrationState.BROKEN, "missing skill-debug managed block"
    expected_fingerprint = _managed_block_fingerprint(body)
    if str(state.get("managed_block_fingerprint", "")).strip() != expected_fingerprint:
        return IntegrationState.BROKEN, "managed block fingerprint does not match SKILL.md"
    return IntegrationState.ATTACHED, None


def _read_skill_frontmatter(skill_path: Path) -> dict[str, object]:
    document = skill_path.read_text(encoding="utf-8")
    if not document.startswith("---\n"):
        return {}
    _, remainder = document.split("---\n", 1)
    if "\n---\n" not in remainder:
        return {}
    frontmatter, _ = remainder.split("\n---\n", 1)
    lines = [line for line in frontmatter.splitlines() if line.strip()]
    data: dict[str, object] = {}
    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def _extract_managed_block_body(document: str) -> str | None:
    if _MANAGED_BLOCK_START not in document or _MANAGED_BLOCK_END not in document:
        return None
    body = document.split(_MANAGED_BLOCK_START, 1)[1].split(_MANAGED_BLOCK_END, 1)[0]
    return body.strip()


def _managed_block_fingerprint(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()
