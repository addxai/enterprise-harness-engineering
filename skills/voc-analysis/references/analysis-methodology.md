# Analysis Methodology

## Table of Contents
1. [Core Principle: LLM Reads ALL Raw Data](#core-principle)
2. [Phase 1: LLM Semantic Tagging](#phase-1-llm-semantic-tagging)
3. [Phase 2: Python Tag Counting](#phase-2-python-tag-counting)
4. [Phase 3: Feature-Level VOC Analysis](#phase-3-feature-level-voc-analysis)
5. [Complete Pipeline](#complete-pipeline)
6. [Iterative Analysis](#iterative-analysis)

---

## Core Principle

**LLM reads ALL raw VOC JSON files directly. No sampling. No pre-filtering. No manual copy-paste.**

| Approach | Coverage | Bias Risk | Quality |
|----------|----------|-----------|---------|
| Manual copy-paste | <1% | Very High | Poor |
| Python pre-filter | 10-20% | High | Medium |
| LLM reads sample (100 items) | <5% | Very High | Poor — Biased |
| **LLM reads ALL data** | **100%** | **None** | **Excellent** |

If a dataset has 8,652 reviews → LLM must read ALL 8,652 reviews.

### What LLM Does (ALL analysis):
- Reads raw JSON files: `reference/*/dataset/*.json`
- Processes every item — posts, comments, reviews, tweets
- Identifies patterns across entire datasets
- Extracts representative quotes with source URLs
- Performs sentiment analysis by reading content
- Tags items semantically (context-aware, not keyword-based)

### What Python Does (ONLY counting):
- Counts tag frequencies from LLM-tagged data
- Calculates percentages and distributions
- Generates cross-tabulations
- Creates visualizations (charts, tables)

**Python does NOT**: read raw data, find patterns, extract quotes, do sentiment analysis, or perform keyword matching.

---

## Phase 1: LLM Semantic Tagging

### Why LLM Tagging, Not Python Keywords

| Python Keyword Matching | LLM Semantic Tagging |
|------------------------|---------------------|
| "battery dies quickly" → misses "power doesn't last" | Both recognized as `battery_drain` |
| Can't understand context: "battery is great!" vs "battery is terrible" | Understands context and sentiment |
| Requires extensive keyword lists | Understands natural language |
| Misses implicit: "I gave up trying to connect" | Tags as `connectivity_issue` + `setup_difficult` |
| False positives: "I love the battery!" → battery_issue | Correctly tags as positive mention |

### Tagging Workflow

**Step 1: Define tag taxonomy**

Define categories upfront based on research topic:

```markdown
Tag Categories:
- Pain Points: connectivity_issue, battery_drain, app_crashes, setup_difficult,
  audio_quality_poor, sync_problems, slow_performance, etc.
- Feature Requests: dark_mode, offline_mode, export_data, custom_alerts, etc.
- Sentiment: positive, negative, neutral, mixed
- User Type: beginner, power_user, professional, casual_user
- Severity: low, medium, high
- Product Aspect: hardware, software, service, support
```

**Step 2: LLM reads and tags ALL items**

Prompt pattern:
```
Read reference/reddit_scraper/dataset/abc123.json

For EVERY post/comment in this file, analyze the content and assign tags:

Tag Categories:
- pain_points (list): [taxonomy above]
- feature_requests (list): [taxonomy above]
- sentiment: positive/negative/neutral/mixed
- user_type: beginner/intermediate/advanced
- severity: low/medium/high

Also identify:
- Top 10 pain points by frequency across ALL items
- 2-3 representative quotes for each pain point WITH URLs
- Overall sentiment distribution

Save tagged data as: reference/tagged/reddit_abc123_tagged.json
```

**Step 3: Output format**

```json
[
  {
    "id": "post_123",
    "text": "The app keeps crashing when I sync photos...",
    "url": "https://reddit.com/r/...",
    "tags": {
      "pain_points": ["app_crashes", "sync_problems"],
      "sentiment": "negative",
      "user_type": "beginner",
      "severity": "high"
    }
  }
]
```

### Best Practices for Tagging

1. **Provide examples** to calibrate tagging:
   ```
   "battery runs out too fast" → battery_drain, severity:high
   "would love a dark mode" → feature_request:dark_mode
   "setup was confusing but support helped" → setup_difficult, sentiment:mixed
   ```

2. **Request confidence scores** when needed:
   ```json
   {"tag": "connectivity_issue", "confidence": 0.95}
   ```

3. **Save tagged data for reuse** — don't re-tag the same dataset

4. **Multi-dataset tagging**: Tag each dataset separately, then combine for analysis

---

## Phase 2: Python Tag Counting

Python is ONLY used after LLM tagging to count frequencies and generate statistics.

### Example Script

```python
import json
from collections import Counter

# Load LLM-tagged data
with open('reference/tagged/reddit_abc123_tagged.json') as f:
    tagged_items = json.load(f)

# Count pain points
pain_points = []
for item in tagged_items:
    pain_points.extend(item['tags'].get('pain_points', []))

counts = Counter(pain_points)

print(f"Top 5 Pain Points (N={len(tagged_items)}):")
for tag, count in counts.most_common(5):
    pct = (count / len(tagged_items)) * 100
    print(f"  {tag}: {count} mentions ({pct:.1f}%)")

# Sentiment distribution
sentiments = [item['tags']['sentiment'] for item in tagged_items]
sentiment_dist = Counter(sentiments)

# Cross-analysis: pain points by user type
for user_type in ['beginner', 'intermediate', 'advanced']:
    segment = [i for i in tagged_items if i['tags'].get('user_type') == user_type]
    segment_pain = Counter()
    for item in segment:
        segment_pain.update(item['tags'].get('pain_points', []))
    print(f"\n{user_type} top pain points:")
    for tag, count in segment_pain.most_common(3):
        print(f"  {tag}: {count}")
```

### What Python Scripts Should Do

- Count tag frequencies
- Calculate percentages
- Generate cross-tabulations (pain_points × user_type)
- Time-series analysis on tagged data (if timestamps available)
- Create bar charts, pie charts, tables
- Export statistics for report

### What Python Scripts Should NOT Do

- Read or analyze raw VOC data
- Perform keyword matching or text analysis
- Do sentiment analysis
- Extract quotes
- Find patterns

---

## Phase 3: Feature-Level VOC Analysis

When comparing products or analyzing specific features in depth, go beyond overall sentiment to compute **per-feature metrics**: mention rate, positive rate, negative rate, and average rating.

### Step 1: Define Feature Keyword Sets

For each feature under analysis, define a keyword set for LLM to identify relevant reviews:

```markdown
Feature: Core Function
  Keywords: detect, detection, recognition, accuracy, ai, smart, identify, alert
Feature: Image Quality
  Keywords: image, photo, video, resolution, night vision, clarity, picture
Feature: App Experience
  Keywords: app, interface, ui, notification, push, crash, slow, buggy
Feature: Connectivity
  Keywords: wifi, connect, disconnect, offline, bluetooth, signal, sync
Feature: Battery
  Keywords: battery, charge, power, solar, last, drain
```

These keywords guide LLM semantic matching — LLM still uses context understanding, not simple string matching.

### Step 2: LLM Tags Feature-Level Data

For each review, LLM tags:
- `features_mentioned`: list of features the review discusses
- `feature_sentiment`: per-feature sentiment (positive/negative/neutral)
- `is_noise`: boolean — whether the review is a noise item (see Noise Filtering below)
- `noise_type`: if noise, what type (e.g., `subscription_complaint`, `shipping_complaint`)

**Extended tagged data schema:**
```json
{
  "id": "review_456",
  "text": "The detection feature is amazing but I hate paying monthly...",
  "url": "https://...",
  "rating": 3,
  "tags": {
    "pain_points": ["subscription_expensive"],
    "positive_aspects": ["detection_accurate"],
    "sentiment": "mixed",
    "features_mentioned": ["core_function", "subscription"],
    "feature_sentiment": {
      "core_function": "positive",
      "subscription": "negative"
    },
    "is_noise": false,
    "noise_type": null
  }
}
```

### Step 3: Noise Filtering

**Problem**: Low-rating reviews often complain about pricing/subscriptions rather than feature quality. Including these in feature quality metrics inflates negative rates.

**Noise Filtering Rules (LLM applies semantically):**

A review is classified as **noise** for a specific feature's quality analysis when ALL of:
1. Rating ≤ 2 stars
2. Primary complaint is about pricing/subscription (not feature quality)
3. No mention of feature quality issues (no "wrong", "inaccurate", "fail", "broken", etc.)

**Examples:**
| Review | Rating | Noise? | Reason |
|--------|--------|--------|--------|
| "Great camera but $5/month is robbery" | 2★ | Yes (for camera quality) | Complaint is pricing, not camera quality |
| "Detection is wrong half the time" | 2★ | No | Genuine quality complaint |
| "Not worth the subscription, plus detection is terrible" | 1★ | No | Contains quality complaint ("detection is terrible") |
| "Love it but too expensive" | 3★ | No (rating > 2) | Rating above noise threshold |

**LLM tags noise items during Phase 1 tagging.** Python excludes them during counting.

### Step 4: Python Calculates Feature-Level Metrics

**Core Formulas:**

```
Mention Rate = reviews mentioning a feature / total reviews
Positive Rate = feature positive count / (valid feature mentions - noise count)
Negative Rate = feature quality negative count / (valid feature mentions - noise count)
Feature Avg Rating = average star rating of reviews mentioning the feature
```

**Python counting script example:**

```python
import json
from collections import Counter, defaultdict

with open('reference/tagged/all_sources_tagged.json') as f:
    items = json.load(f)

features = ['core_function', 'image_quality', 'app_experience', 'connectivity', 'battery']
total = len(items)

print(f"=== Feature-Level VOC Analysis (N={total}) ===\n")
print(f"{'Feature':<20} {'Mentions':>8} {'Rate':>6} {'Pos%':>6} {'Neg%':>6} {'AvgRating':>9}")
print("-" * 65)

for feature in features:
    # Items mentioning this feature
    mentioned = [i for i in items if feature in i['tags'].get('features_mentioned', [])]
    mention_count = len(mentioned)
    mention_rate = mention_count / total * 100 if total else 0

    # Exclude noise items for quality metrics
    effective = [i for i in mentioned if not i['tags'].get('is_noise', False)]
    effective_count = len(effective)

    # Count positive/negative by feature_sentiment
    pos = sum(1 for i in effective if i['tags'].get('feature_sentiment', {}).get(feature) == 'positive')
    neg = sum(1 for i in effective if i['tags'].get('feature_sentiment', {}).get(feature) == 'negative')

    pos_rate = pos / effective_count * 100 if effective_count else 0
    neg_rate = neg / effective_count * 100 if effective_count else 0

    # Average rating for items mentioning this feature
    ratings = [i['rating'] for i in mentioned if 'rating' in i]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    print(f"{feature:<20} {mention_count:>8} {mention_rate:>5.1f}% {pos_rate:>5.1f}% {neg_rate:>5.1f}% {avg_rating:>8.1f}")
```

### Step 5: Feature-Level Competitive Benchmarking

When comparing products, build a **per-feature head-to-head table**:

```markdown
| Feature | Product A Positive Rate | Product A Negative Rate | Product B Positive Rate | Product B Negative Rate | Difference Analysis |
|---------|-------------|-------------|-------------|-------------|---------|
| Core Function | 72% (N=89) | 15% (N=89) | 58% (N=156) | 28% (N=156) | A leads by 14pp |
| Image Quality | 65% (N=45) | 20% (N=45) | 70% (N=112) | 18% (N=112) | B slightly better |
| App Experience | 40% (N=67) | 45% (N=67) | 55% (N=134) | 30% (N=134) | B leads significantly |
```

Rules:
- Always show sample size (N=X) alongside percentages
- Calculate percentage point (pp) differences for quick comparison
- Highlight features where one product significantly leads (>10pp difference)
- Include VOC quotes for each feature organized by positive/negative

### VOC Quote Organization for Features

For each feature, organize quotes by sentiment:

```markdown
#### Core Function VOC

✅ **Positive Reviews (Positive Rate: 72%)**
> "The detection is surprisingly accurate, even in edge cases"
> — ★★★★★ [Amazon Review](https://...)

> "AI correctly detected the target on first try"
> — ★★★★☆ [App Store Review](https://...)

❌ **Negative Reviews (Negative Rate: 15%)**
> "Detection keeps giving false positives"
> — ★★☆☆☆ [Amazon Review](https://...)

🚫 **Filtered Noise (N=12)**
> 12 low-rating reviews only complained about subscription costs without mentioning detection quality; excluded from positive/negative rate calculations.
```

---

## Complete Pipeline

```
Phase 1: LLM Semantic Tagging
  1. Read raw dataset: reference/*/dataset/*.json
  2. Process EVERY item (no sampling)
  3. Tag semantically (pain_points, sentiment, user_type, features_mentioned, feature_sentiment, is_noise)
  4. Extract quotes with URLs
  5. Identify patterns and themes
  6. Save tagged data: reference/tagged/*_tagged.json

Phase 2: Python Overall Counting
  1. Load tagged JSON
  2. Count tag frequencies (pain_points, sentiment, user_type)
  3. Calculate percentages and cross-tabs
  4. Generate visualizations
  5. Export statistics

Phase 3: Feature-Level Analysis (for product comparison or deep-dive)
  1. Define feature keyword sets
  2. LLM tags feature-level sentiment + noise items (done in Phase 1)
  3. Python calculates per-feature metrics: mention rate, positive rate, negative rate, avg rating
  4. Build competitive benchmarking tables (if comparing products)
  5. Organize VOC quotes by feature × sentiment

Phase 4: Report
  1. Combine LLM qualitative insights + Python quantitative stats
  2. Include feature-level comparison tables
  3. Every claim backed by numbers and source links
```

---

## Iterative Analysis

Analysis is not a one-time activity. When preliminary findings raise questions, collect more data.

### When to Collect More Data Mid-Analysis

1. **Unexpected pattern discovered**: "40% mention connectivity" → deep-dive into specific connectivity types
2. **Insufficient sample for a segment**: Only 5 mentions of an issue → need targeted queries
3. **Competitor comparison incomplete**: Own product analyzed but competitors not yet
4. **Hypothesis needs validation**: "Users seem to want feature Y" → search for feature requests
5. **Temporal patterns emerge**: Spike in complaints → investigate what changed
6. **Platform-specific gap**: Reddit analyzed but YouTube comments missing

### Iteration Cycle

```
Initial Data → Preliminary Analysis → Questions/Gaps
    ↑                                        ↓
    └──── Targeted Data Collection ←── Build specific queries
```

### When to Stop

- New data only confirms existing patterns (diminishing returns)
- All major questions are answered
- Coverage meets minimum thresholds (3+ platforms, 5 query layers, 100+ data points)

---

## Example Quantified Finding

**Bad (vague):**
"Many users complained about connectivity issues"

**Bad (keyword matching):**
"Found 45 posts with keyword 'WiFi' or 'connection'"

**Good (LLM tagged + Python counted):**
"43.2% (156/361) of negative reviews were tagged with `connectivity_issue` by semantic analysis, making it the #1 pain point. Of these:
- 67% tagged as high severity
- 45% co-occurred with `setup_difficult`
- Most affected: beginners (65%)
- Average rating: 2.3/5.0 (vs overall 3.8/5.0)

Representative quote:
> 'I spent 3 hours trying to get it connected to my WiFi and it still won't work.'
> — Source: [u/frustrated_user](https://reddit.com/r/example/abc123)"
