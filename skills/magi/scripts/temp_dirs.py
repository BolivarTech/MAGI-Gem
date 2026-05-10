import os
import time

from typing import Optional

MAGI_DIR_PREFIX = "magi-run-"


def create_output_dir(requested_dir: Optional[str] = None) -> str:
    if requested_dir:
        os.makedirs(requested_dir, exist_ok=True)
        return requested_dir

    timestamp = int(time.time())
    new_dir = f"{MAGI_DIR_PREFIX}{timestamp}"
    os.makedirs(new_dir, exist_ok=True)
    return os.path.abspath(new_dir)


def cleanup_old_runs(keep: int) -> None:
    # Minimal cleanup for now
    pass
