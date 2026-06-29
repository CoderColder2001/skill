from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from skill_tools.code_analyse.run_tracking import (  # noqa: E402
    append_run_event,
    finalize_run,
    start_run,
    sync_future_work,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--output-root", type=Path, required=True)
    start_parser.add_argument("--run-id", required=True)
    start_parser.add_argument("--scope-slug", required=True)
    start_parser.add_argument("--objective", required=True)
    start_parser.add_argument("--status", required=True)
    start_parser.add_argument("--module-scoped", action="store_true")

    append_parser = subparsers.add_parser("append-event")
    append_parser.add_argument("--output-root", type=Path, required=True)
    append_parser.add_argument("--run-id", required=True)
    append_parser.add_argument("--phase", required=True)
    append_parser.add_argument("--action", required=True)
    append_parser.add_argument("--evidence", action="append", default=[])
    append_parser.add_argument("--output", dest="outputs", action="append", default=[])
    append_parser.add_argument("--next-step", required=True)

    future_work_parser = subparsers.add_parser("sync-future-work")
    future_work_parser.add_argument("--output-root", type=Path, required=True)
    future_work_parser.add_argument("--scope-slug", required=True)
    future_work_parser.add_argument(
        "--topic",
        action="append",
        default=[],
        help="Topic spec in the form topic|priority|status",
    )

    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("--output-root", type=Path, required=True)
    finalize_parser.add_argument("--run-id", required=True)
    finalize_parser.add_argument("--status", required=True)
    finalize_parser.add_argument("--next-topic", action="append", default=[])

    args = parser.parse_args()
    if args.command == "start":
        start_run(
            output_root=args.output_root,
            run_id=args.run_id,
            scope_slug=args.scope_slug,
            objective=args.objective,
            status=args.status,
            module_scoped=args.module_scoped,
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
            scope_slug=args.scope_slug,
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
    parts = topic_spec.split("|", 2)
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"Invalid topic spec `{topic_spec}`. Expected topic|priority|status."
        )
    topic, priority, status = parts
    return {
        "topic": topic,
        "priority": priority,
        "status": status,
    }


if __name__ == "__main__":
    main()
