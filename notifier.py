from twilio.rest import Client
import logging
from scorer import ScoredJob
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, WHATSAPP_TO

logger = logging.getLogger(__name__)
twilio = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

VERDICT_EMOJI = {
    "APPLY":      "✅",
    "BORDERLINE": "⚠️",
}

def _format_job(scored: ScoredJob, index: int) -> str:
    emoji = VERDICT_EMOJI.get(scored.verdict, "❓")
    budget = scored.job.budget or "Not stated"
    flags = f"🚩 {scored.red_flags}" if scored.red_flags != "None" else ""

    lines = [
        f"{emoji} *{index}. {scored.job.title}*",
        f"💰 {budget} | Score: {scored.score}/10",
        f"📝 {scored.fit_summary}",
        f"💡 {scored.reason}",
    ]
    if flags:
        lines.append(flags)
    lines.append(f"🔗 {scored.job.url}")
    return "\n".join(lines)

def send_digest(scored_jobs: list[ScoredJob], run_label: str) -> None:
    """Send WhatsApp digest. Splits into chunks if many jobs."""
    if not scored_jobs:
        _send(f"🔍 *Upwork Scan — {run_label}*\n\nNo new matching jobs found this round.")
        return

    apply_jobs      = [j for j in scored_jobs if j.verdict == "APPLY"]
    borderline_jobs = [j for j in scored_jobs if j.verdict == "BORDERLINE"]

    header = (
        f"🤖 *Upwork Scan — {run_label}*\n"
        f"✅ {len(apply_jobs)} to apply | ⚠️ {len(borderline_jobs)} borderline\n"
        f"{'─' * 30}"
    )
    _send(header)

    # Send each job as its own message (clean, tappable links)
    for i, scored in enumerate(scored_jobs, 1):
        _send(_format_job(scored, i))

def _send(text: str) -> None:
    try:
        twilio.messages.create(
            from_=TWILIO_FROM,
            to=WHATSAPP_TO,
            body=text,
        )
        logger.info(f"WhatsApp sent: {text[:60]}...")
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
