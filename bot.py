import logging
from fetcher import fetch_jobs
from scorer import score_jobs
from notifier import send_digest
from tracker import load_seen, save_seen, filter_new, mark_seen
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_scan():
    now_label = datetime.utcnow().strftime("%b %d, %H:%M UTC")
    all_jobs = fetch_jobs()
    seen = load_seen()
    new_jobs = filter_new(all_jobs, seen)
    logger.info(f"{len(new_jobs)} new jobs")
    if not new_jobs:
        send_digest([], run_label=now_label)
        return
    scored = score_jobs(new_jobs)
    send_digest(scored, run_label=now_label)
    updated_seen = mark_seen(all_jobs, seen)
    save_seen(updated_seen)

if __name__ == "__main__":
    run_scan()