# Failure Recovery Guide

## Principle

Never skip failed runs. Each failure represents a data gap that needs to be filled — either by fixing the issue, using an alternative actor, or falling back to web search.

---

## Step-by-Step Failure Analysis

### 1. Identify Failed Runs

From cache or API, find runs with status: FAILED, ABORTED, TIMED-OUT.

### 2. Get Run Logs

```bash
curl "https://api.apify.com/v2/actor-runs/{runId}/log?token=$APIFY_TOKEN"
```

### 3. Common Failure Patterns

| Failure Type | Error Keywords | Root Cause | Fix | Web Search Fallback |
|-------------|---------------|------------|-----|-------------------|
| Rate Limit | "429", "Too Many Requests" | Too many requests | Wait 1-2h, retry with lower maxItems | `"[topic] site:[platform].com"` |
| Auth | "401", "403", "login required" | Login needed | Find actor with login support | Search public discussions elsewhere |
| Invalid Input | "Invalid parameter" | Wrong format | Check actor input schema | Verify product exists, get correct IDs |
| Timeout | "TIMED-OUT" | Actor too slow | Reduce maxItems or increase timeout | Web search for smaller sample |
| Actor Bug | "Unexpected error", "null reference" | Actor code issue | Find alternative actor | Web search as workaround |
| Site Change | "Selector not found" | Site UI changed | Find recently updated actor | Web search still works |
| No Data | "No results found" | Query too specific | Broaden query parameters | Verify data exists at all |
| No Scraper | N/A | Platform not supported | Search Apify Store | **Primary: use web search** |

---

## Finding Alternative Actors

### Process

1. **Search by platform**: Search Apify Store or use Agent Skills to find alternative actors
2. **Evaluate alternatives** by:
   - Usage stats (higher = more reliable)
   - Rating (4+ stars preferred)
   - Last updated (within 3 months for social media)
   - Input schema compatibility
   - Pricing
3. **Test with small sample**: maxItems: 10-50
4. **Monitor for 5 minutes** before scaling up

### Evaluation Template

| Actor | Usage | Rating | Last Updated | Cost | Notes |
|-------|-------|--------|-------------|------|-------|
| [failed] | [N] | [X] | [date] | $[X] | FAILED |
| [alt 1] | [N] | [X] | [date] | $[X] | Try this |
| [alt 2] | [N] | [X] | [date] | $[X] | Backup |

---

## Web Search as Universal Fallback

When all actor-based solutions fail, web search is the safety net.

### When Web Search is Better

| Scenario | Web Search | Apify |
|----------|-----------|-------|
| Quick validation | Faster | Slower (setup) |
| Very recent data (<24h) | Real-time | May lag |
| Niche/small sites | Works | No scraper |
| One-off data points | Efficient | Overkill |
| Rate limit issues | No limits | Can be blocked |
| Discovery phase | Flexible | Need exact params |
| Cost concern | Free | Costs money |

### Web Search Recovery Template

```markdown
## Failed Run Recovery: [Platform]

**Original Plan:**
- Actor: [name]
- Target: [what to scrape]
- Goal: [N] items

**Failure:**
- Status: FAILED
- Error: [error message]
- Alternative Actors: [all also fail / none exist]

**Web Search Recovery:**
1. Search: "site:[platform] [topic]"
2. Search: "[topic] [keyword] [year]"
3. Search: "[topic] complaint OR issue OR review"
4. Manually review top [N] results
5. Extract key quotes with URLs

**Result:**
- Collected [N] items (vs target [M])
- Sufficient for [qualitative/limited quantitative] analysis
- Combined with other platform data
```

### Combined Approach (Best Practice)

```
Phase 1: Discovery (Web Search)
  → Find URLs, communities, competitors, ASINs

Phase 2: Bulk Collection (Apify)
  → Run scrapers for structured data at scale

Phase 3: Fallback (Web Search)
  → Fill gaps where scrapers failed
  → Cover platforms without scrapers
```

---

## Decision Tree

```
Failed Apify Run
  ↓
Identify failure type (check logs)
  ↓
Temporary? (rate limit, timeout)
  YES → Wait & retry with adjusted params
  NO  → Search for alternative actors
          ↓
        Found working alternative?
          YES → Use it
          NO  → Web Search fallback
                → Collect critical data points
                → Document in report
```

---

## Proactive Actor Selection (Prevent Failures)

Before creating ANY new run:

1. Search and compare 3-5 actors (don't use the first one)
2. Check recent ratings and reviews for known issues
3. Verify last update date (< 3 months for social media)
4. Test with small sample first (10-50 items)
5. Monitor first 5 minutes before scaling up
6. Have web search queries ready as backup

---

## Documentation

Update cache with failure analysis:

```json
{
  "runId": "abc123",
  "status": "FAILED",
  "actorName": "old-scraper",
  "notes": "Failed: rate limit (429). Switched to new-scraper (run: def456).",
  "alternativeUsed": {
    "actorName": "new-scraper",
    "runId": "def456",
    "reason": "Better rate limit handling"
  }
}
```

For web search fallback, document in the report's methodology section with search queries used, results found, and limitations.
