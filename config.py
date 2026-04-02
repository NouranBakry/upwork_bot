import os

# ── Twilio WhatsApp ────────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN  = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_FROM        = os.environ.get("TWILIO_FROM", "whatsapp:+14155238886")  # sandbox number
WHATSAPP_TO        = os.environ["WHATSAPP_TO"]   # your number e.g. whatsapp:+201XXXXXXXXX

# ── Anthropic ──────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]

# ── Schedule (24h format, Cairo = UTC+3) ───────────────────────────────────
# Runs at 9:00 AM and 6:00 PM Cairo time → 06:00 and 15:00 UTC
SCHEDULE_HOURS_UTC = [6, 15]

# ── Upwork RSS search queries ──────────────────────────────────────────────
# Each query becomes a separate RSS feed — add/remove as needed
SEARCH_QUERIES = [
    "AI agent Python",
    "LangChain FastAPI",
    "AI backend engineer",
    "AI workflow automation Python",
    "OpenAI Claude API integration",
    "AI automation Python FastAPI",
]

# ── Hard filters — skip immediately without scoring ────────────────────────
BUDGET_MINIMUM_FIXED  = 400    # skip fixed-price jobs below this
BUDGET_MINIMUM_HOURLY = 20     # skip hourly jobs below this ($/hr)

REJECT_KEYWORDS = [
    "selenium", "scrapy", "golang", " go ", "ruby", "php",
    "shopify theme", "wordpress plugin", "mobile app", "flutter",
    "react native", "ios developer", "android developer",
    "graphic design", "video editing", "seo",
]

# ── Deduplication file ─────────────────────────────────────────────────────
SEEN_JOBS_FILE = "seen_jobs.json"

# ── Your profile context (fed to Claude for scoring) ──────────────────────
MY_PROFILE = """
Name: Nouran
Stack: Python, FastAPI, LangChain, RabbitMQ, Celery, AWS (S3, Lambda, Secrets Manager)
Experience: Ex-Microsoft senior engineer, 2.5 years on Dynamics 365. 
Now focused on Python AI engineering and distributed systems.
Portfolio: CallSense (AI-powered QA platform), EducateAI (document ingestion + analysis)
Target rate: $35-40/hr for hourly, $500+ for fixed price projects
Strengths: AI agent design, async pipelines, multi-service architecture, LLM integration
Weaknesses / avoid: Selenium-heavy scraping, Go, .NET, mobile dev, no-code only projects
Ideal jobs: AI agents, backend APIs with AI integration, automation pipelines, 
           distributed systems, anything using Claude/OpenAI API seriously
"""
