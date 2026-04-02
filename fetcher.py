import feedparser
import re
import logging
from dataclasses import dataclass
from typing import Optional
from config import SEARCH_QUERIES, BUDGET_MINIMUM_FIXED, BUDGET_MINIMUM_HOURLY, REJECT_KEYWORDS

logger = logging.getLogger(__name__)

RSS_BASE = "https://www.upwork.com/ab/feed/jobs/rss"

@dataclass
class Job:
    id: str
    title: str
    url: str
    description: str
    budget: Optional[str]
    job_type: str        # "Fixed" or "Hourly"
    budget_value: float  # parsed number for filtering
    raw: str             # full description for Claude

def _parse_budget(description: str) -> tuple[str, str, float]:
    """Extract budget type and value from description text."""
    fixed = re.search(r'Budget:\s*\$?([\d,]+)', description, re.IGNORECASE)
    hourly = re.search(r'Hourly Range:\s*\$?([\d.]+)', description, re.IGNORECASE)

    if fixed:
        val = float(fixed.group(1).replace(",", ""))
        return "Fixed", f"${int(val)}", val
    if hourly:
        val = float(hourly.group(1))
        return "Hourly", f"${val}/hr", val
    return "Unknown", "Not stated", 0.0

def _is_hard_rejected(job: Job) -> bool:
    """Immediate disqualification — no Claude call needed."""
    text = (job.title + " " + job.description).lower()

    # Budget too low
    if job.job_type == "Fixed" and 0 < job.budget_value < BUDGET_MINIMUM_FIXED:
        logger.debug(f"Rejected (low budget ${job.budget_value}): {job.title}")
        return True
    if job.job_type == "Hourly" and 0 < job.budget_value < BUDGET_MINIMUM_HOURLY:
        logger.debug(f"Rejected (low hourly ${job.budget_value}): {job.title}")
        return True

    # Stack mismatch
    for kw in REJECT_KEYWORDS:
        if kw.lower() in text:
            logger.debug(f"Rejected (keyword '{kw}'): {job.title}")
            return True

    return False

def fetch_jobs() -> list[Job]:
    """Fetch jobs from all RSS search queries, deduplicated by ID."""
    seen_ids = set()
    jobs = []

    for query in SEARCH_QUERIES:
        url = f"{RSS_BASE}?q={query.replace(' ', '+')}&sort=recency&paging=0%3B15"
        logger.info(f"Fetching RSS: {query}")

        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                job_id = entry.get("id", entry.get("link", ""))
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                desc = entry.get("summary", "")
                job_type, budget_str, budget_val = _parse_budget(desc)

                job = Job(
                    id=job_id,
                    title=entry.get("title", "Untitled"),
                    url=entry.get("link", ""),
                    description=desc[:1500],  # cap for Claude
                    budget=budget_str,
                    job_type=job_type,
                    budget_value=budget_val,
                    raw=f"Title: {entry.get('title','')}\n\nDescription:\n{desc[:2000]}",
                )

                if not _is_hard_rejected(job):
                    jobs.append(job)

        except Exception as e:
            logger.error(f"RSS fetch failed for '{query}': {e}")

    logger.info(f"Fetched {len(jobs)} jobs after hard filters")
    return jobs
