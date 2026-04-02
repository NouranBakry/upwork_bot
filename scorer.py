import anthropic
import json
import logging
from dataclasses import dataclass
from fetcher import Job
from config import ANTHROPIC_API_KEY, MY_PROFILE

logger = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

@dataclass
class ScoredJob:
    job: Job
    verdict: str        # APPLY / BORDERLINE / SKIP
    score: int          # 1–10
    reason: str         # one-line explanation
    red_flags: str      # comma-separated or "None"
    fit_summary: str    # 2-line human-friendly summary

SYSTEM_PROMPT = f"""You are a job filter assistant for a senior AI engineer.
Evaluate Upwork job listings and return a JSON verdict.

Engineer profile:
{MY_PROFILE}

Return ONLY valid JSON in this exact format, no markdown, no extra text:
{{
  "verdict": "APPLY" | "BORDERLINE" | "SKIP",
  "score": <integer 1-10>,
  "reason": "<one sentence why>",
  "red_flags": "<comma-separated issues or 'None'>",
  "fit_summary": "<2 sentences: what the job needs and how well she fits>"
}}

Scoring guide:
- APPLY (7-10): Strong stack match, realistic budget, clear scope, good client signals
- BORDERLINE (4-6): Partial match, uncertain budget, some skill gaps but worth considering
- SKIP (1-3): Wrong stack, too low budget, vague/risky scope, or she'd clearly lose to specialists
"""

def score_job(job: Job) -> ScoredJob | None:
    """Send job to Claude for scoring. Returns None if API call fails."""
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": job.raw}]
        )

        text = response.content[0].text.strip()
        data = json.loads(text)

        return ScoredJob(
            job=job,
            verdict=data.get("verdict", "SKIP"),
            score=int(data.get("score", 0)),
            reason=data.get("reason", ""),
            red_flags=data.get("red_flags", "None"),
            fit_summary=data.get("fit_summary", ""),
        )

    except json.JSONDecodeError as e:
        logger.error(f"Claude returned invalid JSON for '{job.title}': {e}")
        return None
    except Exception as e:
        logger.error(f"Scoring failed for '{job.title}': {e}")
        return None

def score_jobs(jobs: list[Job]) -> list[ScoredJob]:
    """Score all jobs, return only APPLY and BORDERLINE."""
    results = []
    for job in jobs:
        scored = score_job(job)
        if scored and scored.verdict != "SKIP":
            results.append(scored)
            logger.info(f"[{scored.verdict} {scored.score}/10] {job.title}")
        else:
            logger.debug(f"[SKIP] {job.title}")

    # Sort: APPLY first, then by score descending
    results.sort(key=lambda x: (x.verdict != "APPLY", -x.score))
    return results
