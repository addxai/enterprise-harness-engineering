# Apify Agent Skills Setup

## API Key (MANDATORY)

**Apify is the core tool for VOC analysis and must be configured before any research work can begin.**

If you do not have an API Key:

> **Please contact your admin immediately to obtain an APIFY_TOKEN.**
>
> **No Apify API Key = VOC analysis cannot be performed.** This is not optional. Please complete the configuration before starting any research.

## Installation Methods

Apify Agent Skills is the official AI Agent data collection skill set. Source: https://github.com/apify/agent-skills

### Method 1: npx skills install (recommended)

```bash
npx skills add apify/agent-skills
```

This adds all Apify collection skills to your AI coding assistant (supports Claude Code, Cursor, Codex, Gemini CLI, etc.).

### Method 2: Global install to skills directory

**Claude Code:**
```bash
/plugin marketplace add https://github.com/apify/agent-skills
/plugin install apify-ultimate-scraper@apify-agent-skills
```

**Cursor/Windsurf:** Follow the Claude Code format and add to `.cursor/settings.json`

**Gemini CLI/Codex:** Point to `agents/AGENTS.md` or `gemini-extension.json`

### Environment Variable Configuration

After installation, store the API Token in a secret manager.
Expose it only to the current process.
Never print the token or inspect runtime environment files.

```bash
export APIFY_TOKEN=<your-apify-token>
```

**System requirements:**
- Node.js 20.6+

## Quick Verification

After installation, try having the AI assistant perform a simple data collection task to verify:
- "Search Reddit for discussions about [topic]"
- If Apify skills are working correctly, it will return structured collection results

## Available Skills

| Skill | Purpose | Platform Coverage |
|-------|------|---------|
| Universal Scraper | AI-powered universal web scraper | Instagram, Facebook, TikTok, YouTube, Google Maps, Booking.com, TripAdvisor, and 50+ other platforms |
| E-Commerce | E-commerce data collection | Amazon, eBay, etc. (price intelligence, reviews, product research) |
| Social Media Analytics | Social media analysis | Audience analysis, content analysis, influencer discovery, trend analysis |
| Competitor Analysis | Competitive analysis | Brand reputation monitoring, market research |
| Lead Generation | Lead collection | Google Maps, LinkedIn, corporate websites |
| Actor Development | Actor development | Custom Apify Actor development and deployment |

For public X research, use these focused Actor listings:

- [X Tweet Scraper](https://apify.com/xquik/x-tweet-scraper)
- [X Follower Scraper](https://apify.com/xquik/x-follower-scraper)

Their REST selectors are `xquik~x-tweet-scraper` and
`xquik~x-follower-scraper`.

## Apify REST API (Fallback)

When Agent Skills are unavailable, the Apify REST API can still be called directly:

```bash
# List runs
curl "https://api.apify.com/v2/actor-runs" \
  -H "Authorization: Bearer $APIFY_TOKEN"

# Download dataset
curl "https://api.apify.com/v2/datasets/<DATASET_ID>/items?format=json" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -o reference/<scraper_name>/dataset/<DATASET_ID>.json
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| npx skills command not found | Install Node.js: `brew install node` (requires 20.6+) |
| Auth failed | Check that APIFY_TOKEN is correctly set |
| Skills installed but cannot collect | Check network connectivity and token permissions |
| Specific platform collection failed | See `references/failure-recovery.md` for alternatives or Web Search |

## Pricing

Apify Actor pricing models vary.
Check each live Actor listing before running it.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
