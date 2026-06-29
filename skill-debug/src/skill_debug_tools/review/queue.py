from __future__ import annotations

import json
from pathlib import Path

from skill_debug_tools.common.files import atomic_write_text
from skill_debug_tools.review.run import run_review_for_request


def enqueue_review_job(*, runtime_root: Path, request_path: Path, debug_run_id: str) -> Path:
    pending_dir = runtime_root / "review-queue" / "pending"
    job_path = pending_dir / f"{debug_run_id}.json"
    atomic_write_text(
        job_path,
        "{\n"
        f'  "debug_run_id": "{debug_run_id}",\n'
        f'  "request_path": "{request_path}"\n'
        "}\n",
    )
    return job_path


def move_job(*, job_path: Path, destination: str) -> Path:
    target = job_path.parents[1] / destination / job_path.name
    target.parent.mkdir(parents=True, exist_ok=True)
    job_path.replace(target)
    return target


def process_next_review_job(*, runtime_root: Path) -> Path | None:
    pending_dir = runtime_root / "review-queue" / "pending"
    pending_jobs = sorted(pending_dir.glob("*.json"))
    if not pending_jobs:
        return None

    running_job = move_job(job_path=pending_jobs[0], destination="running")
    payload = json.loads(running_job.read_text(encoding="utf-8"))
    request_path = Path(payload["request_path"])
    config_path = runtime_root / "config" / "backends.local.yaml"
    if not config_path.exists():
        config_path = None

    try:
        run_review_for_request(
            request_path=request_path,
            config_path=config_path,
        )
    except Exception:
        return move_job(job_path=running_job, destination="failed")
    return move_job(job_path=running_job, destination="done")
