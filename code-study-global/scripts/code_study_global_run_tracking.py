from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from skill_tools.code_study_global.run_tracking import (  # noqa: E402
    append_run_event,
    finalize_run,
    start_run,
    sync_future_work,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--output-root", type=Path, default=Path("docs/code-study-global"))
    start_parser.add_argument("--run-id", required=True)
    start_parser.add_argument("--objective", required=True)
    start_parser.add_argument("--status", required=True)
    start_parser.add_argument("--focus-topic", action="append", default=[])

    append_parser = subparsers.add_parser("append-event")
    append_parser.add_argument("--output-root", type=Path, default=Path("docs/code-study-global"))
    append_parser.add_argument("--run-id", required=True)
    append_parser.add_argument("--phase", required=True)
    append_parser.add_argument("--action", required=True)
    append_parser.add_argument("--evidence", action="append", default=[])
    append_parser.add_argument("--output", dest="outputs", action="append", default=[])
    append_parser.add_argument("--next-step", required=True)

    future_work_parser = subparsers.add_parser("sync-future-work")
    future_work_parser.add_argument("--output-root", type=Path, default=Path("docs/code-study-global"))
    future_work_parser.add_argument(
        "--topic",
        action="append",
        default=[],
        help="Topic spec: topic|priority|status or topic|priority|status|rationale|suggested_doc",
    )

    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("--output-root", type=Path, default=Path("docs/code-study-global"))
    finalize_parser.add_argument("--run-id", required=True)
    finalize_parser.add_argument("--status", required=True)
    finalize_parser.add_argument("--next-topic", action="append", default=[])

    args = parser.parse_args()
    if args.command == "start":
        start_run(
            output_root=args.output_root,
            run_id=args.run_id,
            objective=args.objective,
            status=args.status,
            focus_topics=args.focus_topic,
        )
        return

    if args.command == "append-event":
        append_run_event(
            output_root=args.output_root,
            run_id=args.run_id,
            phase=args.phase,
            action=args.action,
            evidence=args.evidence,
            outputs=args.outputs,
            next_step=args.next_step,
        )
        return

    if args.command == "sync-future-work":
        sync_future_work(
            output_root=args.output_root,
            topics=[_parse_topic_spec(topic_spec) for topic_spec in args.topic],
        )
        return

    finalize_run(
        output_root=args.output_root,
        run_id=args.run_id,
        status=args.status,
        next_topics=args.next_topic,
    )


def _parse_topic_spec(topic_spec: str) -> dict[str, str]:
    parts = topic_spec.split("|", 4)
    if len(parts) not in {3, 5}:
        raise argparse.ArgumentTypeError(
            f"Invalid topic spec `{topic_spec}`. Expected topic|priority|status or topic|priority|status|rationale|suggested_doc."
        )
    topic, priority, status = parts[:3]
    parsed = {
        "topic": topic,
        "priority": priority,
        "status": status,
    }
    if len(parts) == 5:
        parsed["rationale"] = parts[3]
        parsed["suggested_doc"] = parts[4]
    return parsed


if __name__ == "__main__":
    main()
