---
name: voc-analysis
description: VOC (Voice of Customer) analysis and competitive intelligence research. Collects user feedback from Reddit, Twitter, Amazon, App Store, YouTube, Facebook Groups, Discord, and other platforms via Apify Agent Skills and Web Search, performs semantic tagging, pain point mining, sentiment analysis, and competitive comparison, and generates data-driven market insight reports. Triggers when the user mentions VOC analysis, user feedback analysis, market research, competitive analysis, product review analysis, pain point analysis, customer feedback, competitive intelligence, customer sentiment, review analysis, or needs to collect and analyze user voices from multiple platforms. Should also trigger even if the user just says "check how users rate this product" or "analyze competitors".
---

# VOC Analysis — Market Research and Voice of Customer Analysis

## Description

Senior market research analyst workflow for comprehensive, data-driven VOC (Voice of Customer) analysis and competitive intelligence. Covers the full pipeline: multi-platform data collection (Reddit, Twitter, Amazon, App Store, YouTube, etc.) via Apify Agent Skills and web search, LLM semantic tagging, Python statistical counting, and Chinese report generation with English quotes preserved.

## Prerequisites: Apify API Key (MANDATORY — must be completed first)

**Apify is the core dependency of this Skill. VOC analysis cannot be performed without Apify.**

Before starting ANY research, you MUST verify Apify is configured:

1. Check `APIFY_TOKEN` environment variable: `echo $APIFY_TOKEN`
2. Or check `.env` file for `APIFY_TOKEN=...`

**If no API key is found, STOP IMMEDIATELY. Do NOT proceed. Tell the user:**

> "**This Skill requires Apify for multi-platform data collection. Research cannot begin without an API Key.**
>
> Please follow these steps:
> 1. Contact an admin to obtain an APIFY_TOKEN
> 2. Install Apify Agent Skills: `npx skills add apify/agent-skills`
> 3. Configure environment variable: add `APIFY_TOKEN=<your-token>` to the `.env` file
> 4. Come back to start the research after configuration is complete."

**Apify is not optional.** Web Search alone cannot complete a full VOC analysis (insufficient data volume, no structured collection, unable to cover multiple platforms). Apify must be available before work can begin.

Read `references/apify-setup.md` for detailed installation and configuration steps.

## Rules

1. **Data coverage is everything.** Incomplete data → biased conclusions. Always collect from multiple platforms, build diverse queries, and cross-validate findings. Aim for 5+ query layers and 3+ platforms minimum.

2. **Be a detective, not a tourist.** Don't just check what exists — actively construct 10+ diverse queries. Explore adjacent topics, competitor spaces, and problem-space queries where users describe issues without mentioning the brand.

3. **Analysis is iterative.** Initial data → preliminary analysis → discover gaps/questions → collect targeted data → deeper analysis. It's normal (and expected) to collect more data mid-analysis when patterns or questions emerge.

4. **LLM reads ALL raw data directly.** Point the LLM to raw JSON files and process every single item — no sampling, no pre-filtering, no manual copy-paste. This eliminates bias and ensures complete coverage.

5. **Semantic tagging over keyword matching.** LLM tags items by understanding context (e.g., "I gave up trying to connect it" → `connectivity_issue` + `setup_difficult`). Python is ONLY used to count those tags statistically.

## High-Level Workflow

```
Step 0: Check existing Apify runs (cache-first)
    → Evaluate relevance of each run's input parameters
    → Download only relevant datasets
Step 0.5: Gap analysis (MANDATORY)
    → Map existing data to 5-layer query strategy
    → Identify missing platforms, angles, competitors, time ranges
    → Build 5-10+ new queries to fill gaps
Step 1: Plan query strategy (5 layers)
    → Direct → Problem-space → Competitor → Use-case → Long-tail
Step 2: Collect data (Apify + Web Search fallback)
    → Store in reference/<scraper>/dataset/<id>.json
Step 3: LLM analyzes ALL raw data
    → Reads every item, tags semantically, extracts quotes with URLs
    → Tags feature-level data: features_mentioned, feature_sentiment, is_noise
    → Saves tagged data to reference/tagged/
Step 4: Python counts tags (ONLY statistical counting)
    → Frequencies, percentages, cross-tabs, visualizations
Step 4.5: Feature-Level Analysis (for product comparison)
    → Per-feature metrics: mention rate, positive rate, negative rate, avg rating
    → Noise filtering: exclude subscription/pricing complaints from quality metrics
    → Competitive benchmarking tables with pp differences
Step 5: Generate report in Chinese (English quotes preserved)
    → Save as .md in docs/
```

Each step is detailed in the reference files below.

## Reference Files

Read the relevant reference file when you reach that phase of the workflow:

| File | When to Read | Content |
|------|-------------|---------|
| `references/apify-setup.md` | Before starting | MCP installation, verification, troubleshooting |
| `references/data-collection.md` | Steps 0–2 | Cache management, Python scripts, run checking, dataset download, gap analysis |
| `references/query-strategy.md` | Step 1 | 5-layer query design, platform selection, query examples |
| `references/analysis-methodology.md` | Steps 3–4 | LLM tagging workflow, Python counting, analysis pipeline |
| `references/report-template.md` | Step 5 | Complete report template with all sections |
| `references/failure-recovery.md` | When runs fail | Failure analysis, alternative actors, web search fallback |
| `references/amazon-guide.md` | When scraping Amazon | ASIN search methods, review scraper input formats |

## Data Storage Structure

```
reference/
├── apify_runs_cache.json           # Central cache (keep updated)
├── scripts/                         # Automation scripts
│   ├── build_apify_cache.py        # Fetch all runs + details
│   └── download_datasets.py        # Batch download relevant datasets
├── tagged/                          # LLM-tagged datasets
│   └── <platform>_<id>_tagged.json
├── reddit_scraper/dataset/
├── twitter_scraper/dataset/
├── amazon_reviews/dataset/
├── appstore_reviews/dataset/
├── google_play_reviews/dataset/
├── youtube_scraper/dataset/
└── ...other platforms.../dataset/
```

## Tools

### Primary: IDE Built-in Web Search
- Free, unlimited, real-time — use as primary discovery tool
- Best for: validation, niche platforms, recent events, quick checks
- Always start with web search for discovery before Apify scraping

### Secondary: Apify Agent Skills

Apify provides AI-native agent skills for web scraping and data extraction. Source: https://github.com/apify/agent-skills

**Installation options (choose one):**

1. **npx one-line install (recommended):**
   ```bash
   npx skills add apify/agent-skills
   ```

2. **Global install to skills directory:**
   ```bash
   # Claude Code
   /plugin marketplace add https://github.com/apify/agent-skills
   /plugin install apify-ultimate-scraper@apify-agent-skills
   ```

**Available Skills include:**
- **Universal Scraper** — AI-powered general web scraper (Instagram, Facebook, TikTok, YouTube, Google Maps, and 50+ other platforms)
- **E-Commerce** — E-commerce data collection (Amazon, eBay price intelligence, reviews, product research)
- **Social Media Analytics** — Audience analysis, content analysis, influencer discovery, trend analysis
- **Competitor Analysis** — Competitive analysis, brand reputation monitoring, market research
- **Lead Generation** — B2B/B2C lead collection (Google Maps, LinkedIn, etc.)

**Environment requirements:**
- Node.js 20.6+
- `APIFY_TOKEN` environment variable (set in `.env` file or shell environment)

**Decision tree:**
```
Need data? → Apify skill available?
  YES → Try Apify first → Failed? → Web Search fallback
  NO  → Web Search (primary)
```

See `references/failure-recovery.md` for detailed fallback strategies.

## 5-Layer Query Strategy (Summary)

| Layer | Purpose | Example |
|-------|---------|---------|
| 1. Direct | Brand/product mentions | `"<product_name>" review` |
| 2. Problem-space | Pain points (no brand) | `"smart device not connecting"` |
| 3. Competitor | Competitive products | `"<product_name> vs <competitor>"` |
| 4. Use-case | Target users/scenarios | `r/<community> smart device` |
| 5. Long-tail | Seasonal, niche, integrations | `"<product_name> winter setup"` |

Full details in `references/query-strategy.md`.

## Analysis Approach (Summary)

### What LLM Does (ALL analysis):
- Reads raw JSON files directly (`reference/*/dataset/*.json`)
- Processes EVERY item — no sampling
- Identifies patterns, extracts quotes with URLs
- Performs sentiment analysis by reading content
- Tags items semantically (pain_points, feature_requests, sentiment, user_type)
- Tags **feature-level** data: features_mentioned, feature_sentiment, is_noise
- Saves tagged data to `reference/tagged/`

### What Python Does (ONLY counting):
- Counts tag frequencies from LLM-tagged data
- Calculates percentages and distributions
- Generates cross-tabulations (e.g., pain_points by user_type)
- **Calculates per-feature metrics**: mention rate, positive rate, negative rate, avg rating
- **Excludes noise items** from feature quality metrics (e.g., pure subscription complaints)
- Creates visualizations (charts, tables)

**Python does NOT**: read raw data, find patterns, extract quotes, or do sentiment analysis.

### Feature-Level Analysis (for product comparison):
- Per-feature metrics: mention rate, positive rate, negative rate, avg rating
- Noise filtering: exclude pricing/subscription complaints from feature quality metrics
- Formulas: `positive_rate = positive_count / (valid_mentions - noise_count)`, `negative_rate = quality_negative_count / (valid_mentions - noise_count)`
- Competitive benchmarking: per-feature head-to-head tables with pp differences

Full details in `references/analysis-methodology.md`.

## Report Format (Summary)

- **Language**: Chinese analysis, English quotes preserved verbatim
- **Location**: Save as `.md` in `docs/`
- **Structure**: Executive Summary → Research Strategy → Methodology → Findings → Competitive Intelligence → Sentiment Analysis → User Personas → Recommendations
- **Every claim** must have inline references with clickable URLs
- **Every quote** in original English with source link

Full template in `references/report-template.md`.

## Quality Checklist

### Data Collection
- [ ] Checked cache and existing runs; evaluated relevance
- [ ] **Gap analysis completed** (MANDATORY)
  - [ ] Mapped to 5-layer strategy
  - [ ] Identified platform gaps (target: 3+ of 8 major platforms)
  - [ ] Identified query angle gaps by layer
  - [ ] Coverage percentage calculated
- [ ] Built 5-10+ NEW queries to fill gaps
- [ ] Failed runs analyzed and recovered (see `references/failure-recovery.md`)
- [ ] Final dataset: existing + new ≥ 100 data points

### Analysis
- [ ] LLM read ALL raw JSON files (every item, no sampling)
- [ ] Semantic tagging completed (not keyword matching)
- [ ] Python tag counting completed (frequencies, percentages)
- [ ] Findings quantified (%, counts, averages, sample sizes)
- [ ] All quotes have clickable source URLs
- [ ] Cross-platform validation performed
- [ ] Iterative data collection documented if performed
- [ ] **Feature-level analysis** (if comparing products):
  - [ ] Feature keyword sets defined
  - [ ] Feature-level sentiment tagged (per-feature positive/negative)
  - [ ] Noise items identified and filtered (subscription/pricing complaints)
  - [ ] Per-feature metrics calculated (mention rate, positive rate, negative rate, avg rating)
  - [ ] Competitive benchmarking table with pp differences

### Report
- [ ] Written in Chinese, English quotes preserved
- [ ] Research strategy section explains query logic
- [ ] Each dataset mapped to strategy layer
- [ ] Gap analysis documented
- [ ] Python scripts in appendix (if used)
- [ ] Saved as `.md` in `docs/`

## Examples

**Good Example — Semantic tagging by LLM:**
User review: "I gave up trying to connect it after 2 hours"
→ LLM tags: `connectivity_issue`, `setup_difficult`, sentiment: `negative`
→ Python counts: connectivity_issue appears 47 times (23% of total)

**Bad Example — Python keyword matching:**
User review: "I gave up trying to connect it after 2 hours"
→ Python: `if "connect" in text: tag = "connectivity"` ← misses context, no sentiment, no semantic understanding
→ Misses nuance: "gave up" signals frustration; "2 hours" signals severity

**Good Example — Multi-platform gap analysis:**
After initial Reddit scrape (Layer 1), analyst identifies: no Amazon reviews (Layer 1), no competitor data (Layer 3), no problem-space queries (Layer 2). Builds 8 new queries to fill gaps before proceeding to analysis.

**Bad Example — Single-source analysis:**
Analyst scrapes one Reddit thread, finds 15 comments, writes a report claiming "users love the product" — no gap analysis, no cross-platform validation, insufficient sample size.

## Golden Rules

1. **VOC = LLM reads ALL raw JSON** — never copy-paste or pre-filter
2. **Gap analysis is MANDATORY** — don't skip to analysis without checking coverage
3. **Existing data is never enough** — always build new queries
4. **Research is iterative** — collect more data when questions arise mid-analysis
5. **LLM semantic tagging → Python tag counting** — never use Python keyword matching
6. **Process ENTIRE datasets** — thousands of items, not samples
7. **Every claim needs a number and a source link**
8. **Feature-level analysis for comparisons** — compute per-feature mention rate, positive rate, negative rate; filter noise (subscription complaints) from quality metrics; always show sample size (N=X) with percentages
