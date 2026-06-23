from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from skill_debug_tools.attach import attach_skill
from skill_debug_tools.common.files import atomic_write_text
from skill_debug_tools.workspace.discovery import IntegrationState, discover_skills


def _module_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/skill_debug.py", *args],
        cwd=_module_root(),
        text=True,
        capture_output=True,
        check=False,
    )


def _skill_document(name: str, *, body: str = "# Skill\n") -> str:
    return f"---\nname: {name}\ndescription: test skill\n---\n\n{body}"


def test_skill_debug_list_reports_mixed_states_in_discovery_order(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    zeta_root = workspace / "zeta-skill"
    alpha_root = workspace / "alpha-skill"
    mu_root = workspace / "mu-skill"

    atomic_write_text(zeta_root / "SKILL.md", _skill_document("zeta", body="# Zeta\n"))
    atomic_write_text(alpha_root / "SKILL.md", _skill_document("alpha", body="# Alpha\n"))
    atomic_write_text(mu_root / "SKILL.md", _skill_document("mu", body="# Mu\n"))

    attach_skill(workspace, "alpha")
    attach_skill(workspace, "mu")
    (mu_root / "skill-debug" / "review-prompt.md").unlink()

    result = _run_cli("list", "--workspace-root", str(workspace))

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.splitlines() == [
        f"alpha\tattached\t{alpha_root}",
        f"mu\tbroken\t{mu_root}\tmissing integration files: review-prompt.md",
        f"zeta\tattachable\t{zeta_root}",
    ]


def test_skill_debug_attach_attaches_skill_end_to_end(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    skill_root = workspace / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document("code-analyse", body="# Code Analyse\n"))

    result = _run_cli("attach", "code-analyse", "--workspace-root", str(workspace))

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.strip() == "attached"
    assert (skill_root / "skill-debug" / "config.yaml").exists()
    assert (skill_root / "skill-debug" / "evaluation-guide.md").exists()
    assert (skill_root / "skill-debug" / "review-prompt.md").exists()
    assert (skill_root / "skill-debug" / "injection-state.json").exists()
    records = discover_skills(workspace)
    assert len(records) == 1
    assert records[0].state is IntegrationState.ATTACHED
    assert records[0].reason is None


def test_skill_debug_attach_reports_already_aligned_as_bare_status_token(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    skill_root = workspace / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document("code-analyse", body="# Code Analyse\n"))
    attach_skill(workspace, "code-analyse")

    result = _run_cli("attach", "code-analyse", "--workspace-root", str(workspace))

    assert result.returncode == 0
    assert result.stdout == "already_aligned\n"
    assert result.stderr == ""
    assert (skill_root / "skill-debug" / "config.yaml").exists()


def test_skill_debug_attach_reports_repaired_as_bare_status_token(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    skill_root = workspace / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document("code-analyse", body="# Code Analyse\n"))
    attach_skill(workspace, "code-analyse")
    (skill_root / "skill-debug" / "review-prompt.md").unlink()

    result = _run_cli("attach", "code-analyse", "--workspace-root", str(workspace))

    assert result.returncode == 0
    assert result.stdout == "repaired\n"
    assert result.stderr == ""
    assert (skill_root / "skill-debug" / "review-prompt.md").exists()


def test_skill_debug_attach_reports_unknown_skill_to_stderr_with_stable_nonzero_exit(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    atomic_write_text((workspace / "code-analyse" / "SKILL.md"), _skill_document("code-analyse", body="# Code Analyse\n"))

    result = _run_cli("attach", "missing-skill", "--workspace-root", str(workspace))

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "Unknown skill name 'missing-skill'. Known skills: code-analyse\n"
    assert "Traceback" not in result.stderr


def test_skill_debug_attach_reports_ambiguous_skill_to_stderr_with_stable_nonzero_exit(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    first_root = workspace / "alpha" / "code-analyse-one"
    second_root = workspace / "beta" / "code-analyse-two"
    atomic_write_text(first_root / "SKILL.md", _skill_document("code-analyse", body="# One\n"))
    atomic_write_text(second_root / "SKILL.md", _skill_document("code-analyse", body="# Two\n"))

    result = _run_cli("attach", "code-analyse", "--workspace-root", str(workspace))

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == f"Ambiguous skill name 'code-analyse'. Matches: {first_root}, {second_root}\n"
    assert "Traceback" not in result.stderr
