# Data Collection Workflow

## Table of Contents
1. [Step 0: Check Existing Apify Runs](#step-0-check-existing-apify-runs)
2. [Python Script Approach](#python-script-approach)
3. [Cache File Management](#cache-file-management)
4. [Step 0.5: Gap Analysis](#step-05-gap-analysis)
5. [Step 1-2: Planning and Collection](#steps-1-2-planning-and-collection)
6. [Apify Best Practices](#apify-best-practices)

---

## Step 0: Check Existing Apify Runs (MANDATORY FIRST STEP)

Before doing anything, check for existing runs to avoid duplicate queries and wasted costs.

### Python Script Approach (Recommended)

Writing a Python script to batch-fetch all run details is much faster than sequential tool calls.

**Before writing any script, check if it already exists:**
```bash
ls -la reference/scripts/
```
- If `build_apify_cache.py` exists → use it directly
- If `download_datasets.py` exists → use it directly

#### Script #1: build_apify_cache.py

This script fetches all Apify runs with full details (inputs, actor names) using multi-threading (10 concurrent threads). It does NOT analyze relevance — that's the LLM's job.

**Key features:**
- Fetches all runs via `GET /v2/actor-runs`
- For each run, fetches actor name and input parameters from Key-Value Store
- Uses 10 concurrent threads for speed
- Outputs `reference/apify_runs_cache.json`

**Usage:**
```bash
python reference/scripts/build_apify_cache.py
```

**Output format:**
```json
{
  "last_updated": "2026-01-03T10:30:00Z",
  "total_runs": 45,
  "runs": [
    {
      "id": "abc123",
      "actId": "...",
      "actorName": "reddit-scraper-lite",
      "status": "SUCCEEDED",
      "defaultDatasetId": "<DATASET_ID>",
      "defaultKeyValueStoreId": "...",
      "input": { "searches": ["<product_name>"], "subreddit": "r/<subreddit>" }
    }
  ]
}
```

#### LLM Relevance Analysis (After Script #1)

After the cache is generated, the LLM reads it and evaluates each run's relevance:

**For each run, LLM considers:**
- Do the input keywords/URLs/IDs match the research topic?
- Are there semantic connections (synonyms, related concepts)?
- Is the run status usable (SUCCEEDED, not FAILED/ABORTED)?

**Example LLM reasoning:**
```
Run abc123def456:
- Actor: reddit-scraper-lite
- Input: {"searches": ["<product_name>", "<product_name> Review"]}
- Research Topic: "<product_name> user experience"
- Decision: RELEVANT — direct brand mention

Run xyz789ghi012:
- Actor: tweet-scraper
- Input: {"searchTerms": ["unrelated_product"]}
- Decision: NOT_RELEVANT — different product entirely
```

#### Script #2: download_datasets.py

LLM passes relevant run IDs as command-line arguments. Script downloads datasets in batch.

**Features:**
- Accepts run IDs as CLI arguments
- Automatically waits for RUNNING/READY runs
- Skips FAILED/ABORTED runs
- Organizes by actor type in `reference/<actor>/dataset/`

**Usage:**
```bash
python reference/scripts/download_datasets.py <RUN_ID_1> <RUN_ID_2> ...
```

### Manual API-Based Approach (Fallback)

If Python scripts aren't available:

1. List runs via Apify REST API:
   ```bash
   curl "https://api.apify.com/v2/actor-runs?limit=10&offset=0&desc=true&token=$APIFY_TOKEN"
   ```
   Continue paginating until all runs reviewed.
2. For each relevant run, get details:
   ```bash
   curl "https://api.apify.com/v2/actor-runs/<RUN_ID>?token=$APIFY_TOKEN"
   ```
3. Download dataset:
   ```bash
   curl "https://api.apify.com/v2/datasets/<DATASET_ID>/items?format=json&token=$APIFY_TOKEN" \
     -o reference/<scraper_name>/dataset/<DATASET_ID>.json
   ```

---

## Cache File Management

**File:** `reference/apify_runs_cache.json`

**Maintenance rules:**
- Update `last_updated` whenever cache is modified
- Add new runs immediately after creation
- Update status when runs complete or fail
- Set download info when data is saved locally
- Periodically verify cache accuracy against actual files

**Benefits:**
- Avoid querying Apify API repeatedly (saves time)
- Quickly find relevant historical runs (saves money)
- Filter out irrelevant datasets without downloading
- Track download status across sessions
- Reduce risk of duplicate runs

---

## Step 0.5: Gap Analysis (MANDATORY)

After downloading existing datasets, perform comprehensive gap analysis before proceeding.

### What to Analyze

1. **Platform Coverage**: Which platforms have data? Which are missing?
   - Target: 3+ of 8 major platforms (Reddit, Twitter, Amazon, App Store, Google Play, YouTube, Facebook, Discord)

2. **Query Strategy Layer Coverage**:
   - Layer 1 (Direct Brand): How many queries?
   - Layer 2 (Problem-space): How many?
   - Layer 3 (Competitor): How many?
   - Layer 4 (Use-case): How many?
   - Layer 5 (Long-tail): How many?

3. **Keyword/Topic Coverage**: What's been searched? What's missing?

4. **Time Coverage**: Date range of data? Recent data well-covered?

5. **Competitor Coverage**: Own product + how many competitors?

### Decision Framework

```
IF gaps < 20% of desired coverage:
  → Document gaps, proceed with caveat

IF gaps 20-50%:
  → Build 5-10+ new queries to fill gaps
  → Execute, then proceed

IF gaps > 50%:
  → MUST collect new data before analysis
  → Research would be biased/incomplete
```

### Gap Analysis Output Format

```markdown
## Platform Coverage
| Platform | Status | Datasets |
|----------|--------|----------|
| Reddit   | OK     | 5        |
| Twitter  | Partial| 2        |
| YouTube  | Missing| 0        |
...

## Query Layer Coverage
| Layer | Count | Status |
|-------|-------|--------|
| Direct| 7     | Good   |
| Problem| 1    | Gap    |
| Competitor| 0 | Critical|
...

## Top 5 Critical Gaps
1. Zero competitor analysis
2. No problem-space queries
...

## NEW Queries Needed (10 queries)
[Specific queries with platform, parameters, and rationale]
```

---

## Steps 1-2: Planning and Collection

### Planning Checklist
- [ ] Identify research objectives
- [ ] Define target sources
- [ ] Create diverse query strategy (see `references/query-strategy.md`)
- [ ] Verify no duplicate runs exist

### Collection Guidelines
- Collect from multiple sources (3+ platforms)
- Build diverse queries (5-10+ per research topic)
- Scrape posts AND comments for complete context
- Store in: `reference/<scraper_name>/dataset/<dataset_id>.json`
- Always update cache after any new run or download

### Platform-Specific Tips

**Reddit:**
- Target relevant communities
- Retrieve multiple post types: best/top/new/rising/hot
- Extract full comment threads

**Amazon:** See `references/amazon-guide.md` for ASIN requirements

**Twitter:** Use recent date ranges (last 3-6 months)

**App Store/Google Play:** Focus on 1-star and 5-star reviews for strongest signals

---

## Apify Best Practices

### Do's
- Check cache before creating any new run
- Search for best actor via Apify Agent Skills or Apify Store
- Compare 3-5 actors before choosing (usage, rating, last update)
- Test with small sample first (maxItems: 10-50)
- Update cache immediately after creating/completing runs

### Don'ts
- Don't create duplicate runs without checking cache
- Don't download datasets without checking relevance first
- Don't use the first actor you find — compare alternatives
- Don't ignore failed runs — analyze and recover (see `references/failure-recovery.md`)
- Don't forget to update cache after downloads

### Tracking New Runs
- [ ] Searched for best actor
- [ ] Created run (record actorId, runId, parameters)
- [ ] Added to cache immediately
- [ ] Monitored status
- [ ] Updated cache on completion
- [ ] Downloaded dataset
- [ ] Updated cache with download info
