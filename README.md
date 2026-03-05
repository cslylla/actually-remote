![Actually Remote](assets/banner.png)

# Actually Remote

> A self-hosted job alert bot for jobs that are **actually** remote (not just US-remote).

![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen) ![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-enabled-2088FF)

---

## Table of contents

- [Why this exists](#why-this-exists)
- [How it works](#how-it-works)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Quick start](#quick-start)
- [Configuration guide](#configuration-guide)
- [Usage tips](#usage-tips)
- [Notifications setup](#notifications-setup)
- [Adding companies](#adding-companies)
- [Company Discovery](#company-discovery)
- [How it runs](#how-it-runs)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## Why this exists

The best remote jobs aren't all in San Francisco. Some of the most interesting tech companies in the world are based in Stockholm, Berlin, Prague, Amsterdam, and they hire globally.
The problem isn't the jobs. The problem is finding them.

Job boards are built around the US market. "Remote" means remote in the US. "Europe" means Germany or UK if you're lucky. If you're in Switzerland, Portugal, or anywhere else, you're missing out on great opportunities. And the companies worth working for? Many of them don't bother posting on LinkedIn or Indeed at all. They have a careers page, a few open roles, and no marketing budget for job boards.

**Actually Remote** watches those companies directly. You define the list, set your job titles and location, drop in your CV, and it tells you when something relevant shows up automatically everyday.

---

## How it works

1. You define your target job titles and location keywords in `config.yaml`
2. **Actually Remote** watches your target companies daily (via **GitHub Actions**)
3. Each job passes through a location filter (fast, free, no AI)
4. Matching jobs are scored against your CV by **AI** (fit score, reasons for/against)
5. You receive a daily digest with only relevant matches (email, Discord, or Telegram)
6. Optionally run the discovery agent to expand your list. Use the **AI agent** that searches the web in real time to find remote-friendly companies worth tracking

```
companies.csv → scraper → location filter → AI scoring → your inbox / Discord / Telegram
```

---

## Features

- Smart batch scheduling: 1/7 of companies per day, priority companies checked daily
- Location pre-filtering before AI: fast, free, reduces API usage
- AI CV matching with fit score, reasons for/against, and recommendation
- Pluggable AI provider: Gemini (default), Claude, OpenAI, Ollama
- You can select the right communication channel for you:
  - Daily email digest: one email per day with all matches
  - Discord notifications:one message per job
  - Telegram notifications: one message per job
- Deduplication: never alerts on the same job twice
- `--dry-run` mode: validate URLs, no AI, no cost
- `--test` mode: full pipeline with mock AI, no API cost
- Community-maintained company list: CSV, editable in browser
- PR validation: auto dry-run on `companies.csv` changes
- Zero cost to run: GitHub Actions free tier + Gemini free tier
- **Company discovery agent**: finds new remote-friendly companies you haven't heard of yet using AI + Google Search

---

## Tech stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| Scraping | requests + BeautifulSoup4 |
| AI | Google Gemini (pluggable) |
| Discovery Agent | Google Gemini + Google Search grounding |
| Email | Resend |
| Config | YAML |
| Company list | CSV |
| Scheduling | GitHub Actions |
| Storage | Flat files (no database) |

---

## Quick start

### Step 1: Fork the repo

- Click Fork in the top right
- Set your fork to Private (recommended, it keeps your job search private)
- ⚠️ Important: Go to Settings → Actions → General → set "Workflow permissions" to "Read and write permissions"

### Step 2: Clone your fork locally

```bash
git clone https://github.com/YOUR_USERNAME/actually-remote.git
cd actually-remote
```

### Step 3: Create your config.yaml

```bash
cp config.example.yaml config.yaml
```

Then edit `config.yaml` with your job titles and location keywords. Example:

```yaml
target_titles:
  - "Engineer"
  - "Developer"
  - "Manager"
location_keywords:
  - "Remote"
  - "EMEA"
  - "Europe"
  - "Switzerland"
```

### Step 4: Add your CV

```bash
cp cv.example.txt cv.txt
```

Replace the content with your real CV. Plain text works best, no formatting needed.

### Step 5: Clear seen_jobs.json

⚠️ Important: Replace the contents of `seen_jobs.json` with `{}`. Otherwise you will inherit the author's job history and miss real matches.

### Step 6: Set up notifications

See [Notifications setup](#notifications-setup) below.

### Step 7: Add GitHub Secrets

Go to your repo → Settings → Secrets and variables → Actions. Add these secrets:

| Secret | Value |
|--------|-------|
| GEMINI_API_KEY | Your Gemini API key (free at aistudio.google.com) |
| CONFIG_YAML | Your entire config.yaml file content |
| CV_TEXT | Your entire cv.txt file content |
| RESEND_API_KEY | Your Resend API key (free at resend.com) |
| EMAIL_FROM | Sender email (use onboarding@resend.dev for testing) |
| EMAIL_TO | Your email address |
| DISCORD_WEBHOOK_URL | Your Discord webhook URL (optional) |
| TELEGRAM_BOT_TOKEN | Your Telegram bot token (optional) |
| TELEGRAM_CHAT_ID | Your Telegram chat ID (optional) |

### Step 8: Enable GitHub Actions

Go to the Actions tab in your fork and click: "I understand my workflows, go ahead and enable them"

### Step 9: Test your setup

Run locally first:

```bash
python main.py --dry-run   # validate URLs, no AI needed
python main.py --test      # full pipeline, mock AI, real notifications
```

### Step 10: Go live

Trigger your first real run from the Actions tab: Actions → Daily Job Scraper → Run workflow

---

## Configuration guide

Every option in `config.yaml`:

| Option | Description | Example |
|--------|-------------|---------|
| `ai_provider` | AI provider for CV matching | `gemini` (default), `claude`, `openai`, `ollama` |
| `ai_model` | Model identifier | `gemini-flash-latest` |
| `min_fit_score` | Minimum score for regular companies (1–10) | `7` |
| `priority_min_fit_score` | Minimum score for priority companies — lower threshold since you care more | `6` |
| `target_titles` | Job must contain at least one. Partial matching: "Engineer" matches "Solutions Engineer" | `["Engineer", "Developer"]` |
| `location_keywords` | Job title or description must contain at least one. Runs before AI — fast and free | `["Remote", "EMEA", "Switzerland"]` |
| `notification_channels` | Which channels to use | `[discord, email, telegram]` |
| `email.provider` | Email provider | `resend` |
| `email.send_if_no_matches` | Send "no matches" email when nothing found | `false` |
| `discord.send_if_no_matches` | Send "no matches" summary to Discord | `false` |
| `telegram.send_if_no_matches` | Send "no matches" summary to Telegram | `false` |
| `rotation_days` | Days between scrapes for non-priority companies | `7` |

---

## Usage tips

**Getting better matches:**

- Use partial keywords: "Engineer" catches all engineer roles
- Add your target companies as `priority: true` for daily checking
- Start with a broad location list, narrow down if too noisy
- Lower `priority_min_fit_score` for companies you really want

**Understanding the batch schedule:**

- By default, 1/7 of your company list is checked each day, full cycle every week
- Mark companies as priority: true to check them every single day
- Checking too frequently can trigger bot detection on some career pages
- Small list (under 20 companies)? Set rotation_days: 1 to check everything daily
- When in doubt, use priority: true for the companies you really care about

**Managing your company list:**

- Use the default list as a starting point
- Delete companies in sectors you don't care about
- Add your dream companies as `priority: true`
- Pull upstream updates periodically to get new community companies:

```bash
git remote add upstream https://github.com/cslylla/actually-remote
git pull upstream main
```

**Managing notifications:**

- Enable `send_if_no_matches: true` initially to confirm it's running
- Disable it once you trust the setup
- Use Discord for instant alerts, email for daily digest

**Running costs:**

- Gemini free tier: 1,500 requests/day — sufficient indefinitely
- GitHub Actions free tier: sufficient for daily runs
- Resend free tier: 100 emails/day — more than enough
- Total cost: $0/month

---

## Notifications setup

### Email (Resend) — recommended

1. Create free account at [resend.com](https://resend.com)
2. Create an API key
3. Add `RESEND_API_KEY`, `EMAIL_FROM`, `EMAIL_TO` to GitHub Secrets
4. Add `email` to `notification_channels` in config.yaml

### Discord

1. Open Discord → your server → Edit Channel → Integrations → Webhooks
2. Create webhook, copy URL
3. Add `DISCORD_WEBHOOK_URL` to GitHub Secrets
4. Add `discord` to `notification_channels` in config.yaml

### Telegram

1. Search @BotFather in Telegram
2. Send `/newbot` and follow instructions
3. Send a message to your new bot
4. Visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Copy your chat ID from the response
6. Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to GitHub Secrets
7. Add `telegram` to `notification_channels` in config.yaml

---

## Adding companies

`companies.csv` is a community resource. You can:

- Edit directly in the GitHub browser, no terminal needed
- Submit a PR — the `validate_companies` workflow runs `--dry-run` automatically
- See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines

**What qualifies:** Companies with global/EMEA/rest of world remote roles and a direct careers page (no login required). No US-only companies, no generic job boards.

---

## Company Discovery

**Actually Remote** ships with a curated list of 100+ companies. But the **discovery agent** can find companies you haven't heard of yet.

Run it manually whenever you want to expand your list:

```
python discover.py
```

The agent searches Ashby, Greenhouse, and Lever job boards using your `target_titles` and `location_keywords` from `config.yaml`.

**What it does:**

- Runs up to 6 search queries combining your job titles and locations
- Uses Gemini with Google Search to find matching companies
- Filters out companies already in your `companies.csv`
- Validates each URL is accessible before suggesting it
- Sends results via your configured notification channels
- Saves results to `discovery_results.txt`

**Output example:**

```
🔍 Actually Remote — Discovery Run
Found 7 new companies to consider:

- Paddle — https://paddle.com/careers
- Wasabi Technologies — https://boards.greenhouse.io/wasabi
- Stripe — https://stripe.com/jobs
```

**Important — free tier limits:**

The discovery agent uses your Gemini API key. On the free tier:

- Gemini 2.5 Flash: 5 requests per minute
- Gemini 2.5 Flash Lite: 10 requests per minute
- Running 6 queries uses 6 requests (within limits)
- Avoid running it multiple times in quick succession
- Do not run it on the same day as heavy scraper testing

**Adding discoveries to your list:**

Review the suggestions and add the ones you want to `companies.csv`. Either edit directly in GitHub browser or locally. The discovery agent doe not modify your `companies.csv` automatically.

---

## How it runs

- **Schedule:** Daily at 5am UTC (6am CET)
- **Manual trigger:** Available from Actions tab
- **Batch rotation:** 1/7 of companies per day; each company checked once per week
- **Priority companies:** Checked every day
- **seen_jobs.json:** Auto-committed after each run (persists state)
- **Failure notification:** GitHub automatically emails you when the workflow fails (and you will get a Discord notification, if Discord is configured)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

Three ways to contribute:

1. Add companies to `companies.csv`
2. Report broken URLs (use the Broken URL issue template)
3. Code improvements: open an issue first to discuss

PRs that touch `companies.csv` are automatically validated with `--dry-run`.

---

## Roadmap

- [x] Core scraper with batch rotation
- [x] AI CV matching (Gemini)
- [x] Email digest (Resend)
- [x] Discord notifications
- [x] Telegram notifications
- [x] GitHub Actions automation
- [x] Community company list with PR validation
- [x] Company discovery agent (search Ashby/Greenhouse/Lever)
- [ ] Playwright support for JS-heavy career pages
- [ ] Gmail SMTP support
- [ ] Slack notifications

---

## License

[MIT License](LICENSE)

`companies.csv` is a community resource. Contributions welcome, see [CONTRIBUTING.md](CONTRIBUTING.md).
