import logging
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from fetcher import fetch_jobs
from scorer import score_jobs
from notifier import send_digest
from tracker import load_seen, save_seen, filter_new, mark_seen
from config import SCHEDULE_HOURS_UTC

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log"),
    ]
)
logger = logging.getLogger(__name__)


def run_scan():
    logger.info("=" * 50)
    logger.info("Starting Upwork job scan...")

    now_label = datetime.utcnow().strftime("%b %d, %H:%M UTC")

    try:
        # 1. Fetch from RSS
        all_jobs = fetch_jobs()

        # 2. Filter out already-seen jobs
        seen = load_seen()
        new_jobs = filter_new(all_jobs, seen)
        logger.info(f"{len(new_jobs)} new jobs after deduplication")

        if not new_jobs:
            send_digest([], run_label=now_label)
            return

        # 3. Score with Claude
        scored = score_jobs(new_jobs)
        logger.info(f"{len(scored)} jobs worth sending")

        # 4. Send WhatsApp digest
        send_digest(scored, run_label=now_label)

        # 5. Mark all fetched jobs as seen (even SKIPs — don't re-evaluate)
        updated_seen = mark_seen(all_jobs, seen)
        save_seen(updated_seen)

    except Exception as e:
        logger.error(f"Scan failed: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Upwork Job Bot starting...")

    # Run once immediately on startup
    run_scan()

    # Then schedule for 9am and 6pm Cairo (06:00 and 15:00 UTC)
    scheduler = BlockingScheduler(timezone="UTC")
    for hour in SCHEDULE_HOURS_UTC:
        scheduler.add_job(
            run_scan,
            CronTrigger(hour=hour, minute=0),
            id=f"scan_{hour}",
            name=f"Upwork scan at {hour}:00 UTC",
        )

    logger.info(f"Scheduler running. Next scans at UTC hours: {SCHEDULE_HOURS_UTC}")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
