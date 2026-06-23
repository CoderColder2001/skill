from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from skill_debug_tools.attach import attach_skill
from skill_debug_tools.workspace import discover_skills


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--workspace-root", type=Path, required=True)

    attach_parser = subparsers.add_parser("attach")
    attach_parser.add_argument("skill_name")
    attach_parser.add_argument("--workspace-root", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "list":
        return _list_skills(args.workspace_root)
    return _attach_skill(args.workspace_root, args.skill_name)


def _list_skills(workspace_root: Path) -> int:
    for record in discover_skills(workspace_root):
        line = f"{record.name}\t{record.state.value}\t{record.root}"
        if record.reason:
            line = f"{line}\t{record.reason}"
        print(line)
    return 0


def _attach_skill(workspace_root: Path, skill_name: str) -> int:
    try:
        result = attach_skill(workspace_root=workspace_root, skill_name=skill_name)
    except (ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
