import json
import os
import logging
from config import SEEN_JOBS_FILE

logger = logging.getLogger(__name__)

def load_seen() -> set[str]:
    if not os.path.exists(SEEN_JOBS_FILE):
        return set()
    try:
        with open(SEEN_JOBS_FILE) as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_seen(seen: set[str]) -> None:
    # Keep only last 2000 IDs to prevent unbounded growth
    ids = list(seen)[-2000:]
    try:
        with open(SEEN_JOBS_FILE, "w") as f:
            json.dump(ids, f)
    except Exception as e:
        logger.error(f"Failed to save seen jobs: {e}")

def filter_new(jobs, seen: set[str]) -> list:
    """Return only jobs not seen before."""
    return [j for j in jobs if j.id not in seen]

def mark_seen(jobs, seen: set[str]) -> set[str]:
    """Add job IDs to seen set."""
    return seen | {j.id for j in jobs}
