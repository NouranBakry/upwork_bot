# Upwork Job Alert Bot 🤖

Monitors Upwork RSS feeds twice daily, scores jobs with Claude, and sends matching opportunities to WhatsApp.

## How it works

1. Fetches jobs from Upwork RSS across multiple search queries
2. Hard-filters low-budget and wrong-stack jobs instantly
3. Scores remaining jobs with Claude against your profile
4. Sends APPLY ✅ and BORDERLINE ⚠️ jobs to WhatsApp — SKIPs are silent

## Setup

### 1. Clone and install
```bash
pip install -r requirements.txt
```

### 2. Environment variables
Set these in Railway (or a local `.env`):

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM=whatsapp:+14155238886        # Twilio sandbox number
WHATSAPP_TO=whatsapp:+201XXXXXXXXX       # Your WhatsApp number
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Twilio WhatsApp Sandbox
- Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message
- Send the join code from your WhatsApp to activate the sandbox
- Use `whatsapp:+14155238886` as the from number

### 4. Deploy to Railway
```bash
# Push to GitHub, connect repo in Railway
# Add environment variables in Railway dashboard
# Railway uses Procfile → runs: python bot.py
```

## Schedule
- Runs at **9:00 AM Cairo time** (06:00 UTC)  
- Runs at **6:00 PM Cairo time** (15:00 UTC)
- Also runs once immediately on startup

## Customization

Edit `config.py` to:
- Add/remove `SEARCH_QUERIES`
- Adjust `BUDGET_MINIMUM_FIXED` and `BUDGET_MINIMUM_HOURLY`
- Add keywords to `REJECT_KEYWORDS`
- Update `MY_PROFILE` as your stack evolves

## Estimated cost
- Upwork RSS: free
- Twilio sandbox: free (production ~$0.005/message)
- Claude API: ~$0.002 per job scored → pennies per day
- Railway: free tier covers this easily
