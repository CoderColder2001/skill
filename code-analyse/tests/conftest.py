from __future__ import annotations

import sys
from pathlib import Path

import pytest

FRAMEWORK_SRC_ROOT = Path(__file__).resolve().parents[2] / "skill-debug" / "src"
if str(FRAMEWORK_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_SRC_ROOT))


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    return repo_root


@pytest.fixture
def code_analyse_output_root(temp_repo: Path) -> Path:
    return temp_repo / "code-analyse-docs"


@pytest.fixture
def skill_debug_logs_root(temp_repo: Path) -> Path:
    return temp_repo / "skill-debug-logs"


@pytest.fixture
def skill_debug_runtime_root(temp_repo: Path) -> Path:
    return temp_repo / "skill-debug" / "runtime"
