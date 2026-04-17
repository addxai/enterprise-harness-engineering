# 5-Layer Query Strategy

## Design Principles

Don't just rely on existing data. Actively construct 10+ diverse queries from multiple angles. Coverage beats convenience — thorough beats fast.

---

## Layer 1: Direct Brand/Product Queries

**Purpose:** Capture explicit product/brand discussions.

**Keyword logic:** Product names, brand variants, common nicknames, model numbers.

**Examples:**
- Reddit: `searches: ["Brand Name", "Brand Name review", "Brand Name issue"]`
- Twitter: `searchTerms: ["Brand Name", "#BrandName"]`
- Amazon: Own product ASIN (see `references/amazon-guide.md`)
- App Store: Own app ID

**What you'll find:** Direct feedback, reviews, support requests, feature discussions.

---

## Layer 2: Problem-Space Queries

**Purpose:** Discover user pain points even when they don't mention the brand. Users often describe problems without naming the product.

**Keyword logic:** Start from known issues, think how users naturally describe problems.

**Examples:**
- `"[product type] not working"`, `"[product type] keeps disconnecting"`
- `"[feature] issues"`, `"why does my [product type] keep [problem]"`
- `"[product type] setup help"`, `"[product type] troubleshooting"`

**What you'll find:** Unbranded complaints, workarounds, alternative-seeking behavior.

---

## Layer 3: Competitive Analysis Queries

**Purpose:** Understand competitive landscape and user comparisons.

**Competitor identification:**
- Direct competitors (same product category)
- Alternative solutions (different approach, same problem)
- Aspirational competitors (market leaders users compare to)

**Examples:**
- `"Product A vs Product B"`, `"alternative to [Brand]"`
- `"best [product type] 2024"`, `"[Brand] competitor"`
- Amazon: Competitor ASINs (reviews), `"Customers also viewed"` products
- App Store: Competitor apps in same category

**What you'll find:** Feature comparisons, switching reasons, market positioning.

---

## Layer 4: Use-Case / Target User Queries

**Purpose:** Understand user motivations, usage environments, and target communities.

**Scenario identification:** Who uses it? Where? Why? In what context?

**Examples:**
- Target communities: `r/[hobby]`, `r/[profession]`, Facebook Groups
- Use-case keywords: `"[product type] for [use case]"`, `"[product type] at [location]"`
- Persona-based: `"beginner [product type]"`, `"professional [product type] setup"`

**What you'll find:** Real usage contexts, unmet needs, community dynamics.

---

## Layer 5: Long-Tail / Niche Queries

**Purpose:** Discover unexpected insights from edge cases.

**Construction logic:** Seasonal concerns, specific technical issues, integrations, regional topics.

**Examples:**
- Seasonal: `"[product] winter"`, `"[product] rainy season"`
- Integration: `"[product] with [other product]"`, `"[product] HomeKit"`
- Specific issues: `"[product] software update problem"`, `"[product] error code [X]"`
- Regional: `"[product] Europe shipping"`, `"[product] Asia availability"`

**What you'll find:** Niche pain points, seasonal patterns, integration opportunities.

---

## Platform Selection Guide

| Platform | Best For | Sorting Strategy | Tips |
|----------|----------|-----------------|------|
| Reddit | Deep discussions, troubleshooting | hot/top (pain points) + new (latest) | Target specific subreddits |
| Twitter/X | Real-time feedback, sentiment | Latest, past 3-6 months | Brand mentions + sentiment words |
| Amazon Reviews | Post-purchase feedback | recent + helpful; focus 1★ and 5★ | Requires ASIN |
| App Store | App-specific bugs, features | Recent, by rating segment | Use app ID |
| Google Play | Android user feedback | Same as App Store | Check competitor apps too |
| YouTube | Video content, unboxing | Sort by views/recent | Scrape comment sections |
| Facebook Groups | Community discussions | Active groups, recent posts | Product-specific + hobby groups |
| Discord/Slack | Power users, tech discussions | Active servers/channels | Official + community channels |
| Trustpilot | Service/brand trust | Recent, by star rating | Good for B2C services |

---

## Query Iteration Process

```
Round 1: Execute Layer 1-2 queries
    ↓
Round 2: Analyze preliminary results → identify gaps
    ↓
Round 3: Execute Layer 3-5 queries based on gaps
    ↓
Round 4: Deep-dive queries on discovered patterns
    ↓
Round 5: Cross-validate across platforms
```

**Iteration triggers:**
- Discovered unexpected pattern → build targeted deep-dive queries
- Insufficient sample for a segment → create specific queries
- Competitor comparison incomplete → add competitor product queries
- Temporal pattern found → collect historical data with date filters

---

## Web Search Integration

Web search complements Apify scraping — use both together:

**Discovery phase (Web Search):**
```
"[brand] review" → Find review sites, communities, competitors
"[brand] site:reddit.com" → Identify relevant subreddits
"[brand] site:amazon.com" → Find product ASINs
"alternative to [brand]" → Discover competitors
```

**Bulk collection (Apify):**
- Use discovered URLs/IDs as Apify actor inputs
- Scrape hundreds/thousands of structured items

**Fallback (Web Search):**
- When Apify actors fail or don't exist for a platform
- For niche sites, forums, Lemmy, Mastodon, etc.

**Site-specific search operators:**
```
site:reddit.com "[brand]"
site:amazon.com "[product type]"
site:youtube.com "[brand] review"
"[brand]" AND (complaint OR issue OR problem)
"[brand]" -advertisement -sponsored
intitle:"[brand] review"
```

---

## Minimum Query Coverage

For a thorough research report, aim for:

| Dimension | Minimum | Ideal |
|-----------|---------|-------|
| Query layers | 3 of 5 | 5 of 5 |
| Platforms | 3 | 5+ |
| Total queries | 5 | 10+ |
| Total data points | 100 | 500+ |
| Competitor products | 2 | 3-5 |
| Time range | 3 months | 6-12 months |
