# Report Template

Write the report in Chinese. Keep all quotes and references in original English.

---

```markdown
# [Topic] Market Research Report

## Executive Summary
[3-5 bullet points summarizing key findings]

## Research Strategy

### Research Objectives
- Question 1: [e.g., What are users' biggest pain points?]
- Question 2: [e.g., Strengths and weaknesses compared to competitors?]
- Question 3: [e.g., What features do users need most?]

### Query Strategy Design

#### Layer 1: Direct Brand Queries
- **Purpose**: Obtain discussions directly related to the product
- **Keyword logic**: [Product name, brand variants, common nicknames]
- **Query examples**: [Specific queries]

#### Layer 2: Problem-Space Queries
- **Purpose**: Discover user pain points (users may not mention the brand)
- **Keyword logic**: [Starting from known problems]
- **Query examples**: [Specific queries]

#### Layer 3: Competitive Analysis Queries
- **Purpose**: Understand the competitive landscape
- **Competitor identification logic**: [Direct competitors, alternatives]
- **Query examples**: [Specific queries]

#### Layer 4: Use-Case Queries
- **Purpose**: Understand user motivations and usage context
- **Scenario identification logic**: [Who uses it, where, why]
- **Query examples**: [Specific queries]

#### Layer 5: Long-Tail/Niche Queries
- **Purpose**: Discover unexpected insights
- **Construction logic**: [Seasonal, specific issues, integrations]
- **Query examples**: [Specific queries]

#### Platform Selection Logic

| Platform | Selection Reason | Sort Strategy |
|------|---------|---------|
| Reddit | [Reason] | hot/top + new |
| Twitter | [Reason] | Latest, past 3-6 months |
| Amazon Reviews | [Reason] | recent + helpful |
| ... | ... | ... |

### Query Iteration Process
1. Initial queries: [What was discovered]
2. Gap analysis: [What gaps were identified]
3. Supplementary queries: [What was explored deeper]
4. Mid-analysis additional collection: [What extra data was needed during analysis]
5. Final confirmation: [How cross-validation was performed]

## Research Methodology

### Analysis Method

This research uses the LLM direct raw VOC data reading method:
1. LLM directly reads all raw JSON files (every item analyzed, no sampling)
2. LLM performs semantic tagging (pain points, feature requests, sentiment, user type, etc.)
3. Python counts tag frequencies (counting only, no analysis)

### Data Source Details

#### 1. Reddit Data
- **Actor**: [actor_id]
- **Dataset ID**: [dataset_id]
- **Strategy layer**: Layer [N]
- **Query logic**: [Why these keywords/communities were chosen]
- **Query parameters**: searches: `[keywords]`, subreddit: `r/[community]`, maxItems: [N]
- **Apify Run Link**: https://console.apify.com/actors/runs/[runId]
- **Dataset Link**: https://console.apify.com/storage/datasets/[dataset_id]
- **Local path**: `reference/reddit_scraper/dataset/[dataset_id].json`
- **Collection date**: [date]
- **Data volume**: [N] posts, [M] comments

#### 2. Amazon Reviews Data
- **Actor**: [actor_id]
- **Dataset ID**: [dataset_id]
- **Strategy layer**: Layer [N]
- **Query logic**: [Why these products were chosen]
- **Product analysis list**:
  | Product | ASIN | Category | Amazon Link |
  |------|------|------|------------|
  | [Own product] | [ASIN] | Own | https://amazon.com/dp/[ASIN] |
  | [Competitor 1] | [ASIN] | Competitor | https://amazon.com/dp/[ASIN] |
- **Query parameters**: ASINs: `[list]`, maxReviews: [N], country: [US], sortBy: [recent]
- **ASIN acquisition method**: [How these ASINs were found]
- **Apify Run Link**: https://console.apify.com/actors/runs/[runId]
- **Local path**: `reference/amazon_reviews/dataset/[dataset_id].json`
- **Collection date**: [date]
- **Data volume**: [N] reviews
- **Rating distribution**: [X% 5-star, Y% 4-star, Z% 3-star, W% 2-star, V% 1-star]

#### 3. [Other Platform Data...]
[Same format]

#### N. Web Search Data (if used)
- **Platform/topic**: [platform]
- **Data source**: Web Search
- **Strategy layer**: Layer [N]
- **Reason for use**: [No Apify Actor / Actor failed / quick validation]
- **Search queries**:
  ```
  Query 1: "[topic] site:[platform].com"
  Query 2: "[product] [keyword] [year]"
  ```
- **Collection method**: Manual review of top [N] search results
- **Data volume**: [N] discussions/comments
- **Collection date**: [date]
- **Limitations**: Non-exhaustive collection, focused on high-quality content

### Query Strategy Coverage Summary

| Strategy Layer | Coverage Status | Dataset Count |
|--------|---------|-----------|
| Layer 1 (Direct Brand) | OK/Partial/Missing | [N] |
| Layer 2 (Problem-Space) | OK/Partial/Missing | [N] |
| Layer 3 (Competitive) | OK/Partial/Missing | [N] |
| Layer 4 (Use-Case) | OK/Partial/Missing | [N] |
| Layer 5 (Long-Tail Niche) | OK/Partial/Missing | [N] |

### Gap Analysis and Data Completeness

**Initial coverage**: [X%]
**Final coverage**: [Y%]
**Improvement**: [+Z%]
**Total datasets**: Existing ([N]) + New ([N]) = [Total]

### Iterative Data Collection (if applicable)

[Document issues found during analysis and additional data collected]

### Failed Run Recovery (if applicable)

| Failed Run | Actor | Failure Reason | Recovery Plan | Result |
|----------|-------|---------|---------|------|
| [runId] | [actor] | [reason] | [plan] | OK/Failed |

### Data Statistics
- **Total sample size**: [total]
- **Time range**: [date range]
- **Platform coverage**: [platforms]
- **Tools**: Apify Actors + Web Search

## Key Findings

### Finding 1: [Category]

**Quantified data:**
- Mention frequency: X times (Y% of total sample)
- Sentiment distribution: Z% positive, W% negative, V% neutral
- Average rating: N/5.0 (sample size=M)

[Detailed analysis]

**User quotes:**
> "[exact English quote]"
> - Source: [Post Title](https://direct-link.com)

**Analysis:**
[Analysis text]

### Finding 2: [Category]
[Same format...]

## Competitive Analysis

### Competitive Comparison Matrix

| Metric | Own Product | Competitor A | Competitor B |
|------|---------|--------|--------|
| Average Rating | X.X/5.0 (N reviews) | Y.Y/5.0 (M reviews) | Z.Z/5.0 (K reviews) |
| Positive Mention Rate | XX% | YY% | ZZ% |
| Main Strengths | [Data-backed] | [Data-backed] | [Data-backed] |
| Main Pain Points | [Data-backed] | [Data-backed] | [Data-backed] |

### Feature-Level VOC Comparison

Per-feature comparison of each product's mention rate, positive rate, negative rate, and average rating. Noise reviews (e.g., pure subscription/pricing complaints) have been excluded from positive/negative rate calculations.

**Formula explanation:**
- Mention Rate = reviews mentioning the feature / total reviews
- Positive Rate = feature positive count / (valid mentions - noise count)
- Negative Rate = feature quality negative count / (valid mentions - noise count)

#### Feature 1: [Feature Name]

| Metric | Own Product | Competitor A | Competitor B | Difference Analysis |
|------|---------|--------|--------|---------|
| Mention Rate | XX% (N=XX) | YY% (N=YY) | ZZ% (N=ZZ) | [Who is discussed more] |
| Positive Rate | XX% | YY% | ZZ% | [Leads/trails by Xpp] |
| Negative Rate | XX% | YY% | ZZ% | [Leads/trails by Xpp] |
| Feature Avg Rating | X.X/5.0 | Y.Y/5.0 | Z.Z/5.0 | |
| Noise Filtered | N items | N items | N items | |

**VOC Quotes:**

Positive reviews for own product:
> "[English quote]"
> — 5-star [Source](https://...)

Negative reviews for own product:
> "[English quote]"
> — 2-star [Source](https://...)

Positive reviews for Competitor A:
> "[English quote]"
> — 5-star [Source](https://...)

Negative reviews for Competitor A:
> "[English quote]"
> — 1-star [Source](https://...)

#### Feature 2: [Feature Name]
[Same format...]

#### Feature Dimension Overall Comparison

| Feature | Own Positive Rate | Own Negative Rate | Competitor A Positive Rate | Competitor A Negative Rate | Difference (pp) |
|---------|-----------|-----------|------------|------------|----------|
| [Feature 1] | XX% (N=X) | XX% | YY% (N=Y) | YY% | +/-Xpp |
| [Feature 2] | XX% (N=X) | XX% | YY% (N=Y) | YY% | +/-Xpp |
| [Feature 3] | XX% (N=X) | XX% | YY% (N=Y) | YY% | +/-Xpp |

## User Sentiment Analysis

### Overall Sentiment Distribution
- Positive: X% (N items)
- Neutral: Y% (M items)
- Negative: Z% (K items)
- Total sample: [total]

### Top 5 Positive Themes
1. [Theme]: XX mentions (YY%)
2. ...

### Top 5 Negative Themes / Pain Points
1. [Pain Point]: XX mentions (YY%), avg rating: Z.Z/5.0
2. ...

### Feature Requests (sorted by mention frequency)
1. [Feature]: XX mentions
2. ...

## User Persona Analysis

### Persona 1: [Name]

**Profile:**
- **Segment share**: XX% (N=XXX)
- **Primary platform**: [platform] (XX%)
- **Average rating**: X.X/5.0

**Quantified characteristics:**
- XX% mention [specific pain point]
- YY% request [specific feature]

**Representative quote:**
> "[English quote]"
> - Source: [Username](https://link)

### Cross-Persona Comparison

| Metric | Persona 1 | Persona 2 | Persona 3 |
|------|-----------|-----------|-----------|
| Share | XX% | YY% | ZZ% |
| Rating | X.X | Y.Y | Z.Z |
| Top Pain Point | [Issue] | [Issue] | [Issue] |

## Recommendations

### P0 - Immediate Action (affects >30% of users)
1. **[Recommendation]**
   - Data support: XX% of users mentioned
   - Rating impact: Decreases rating by Y.Y points
   - Expected outcome: Improve Z% satisfaction

### P1 - High Priority (affects 10-30% of users)
[...]

### P2 - Medium Priority (affects <10% but important)
[...]

## Appendix

### Quantitative Analysis Code
[Python scripts used]

### Complete Dataset List
- `reference/[scraper]/dataset/[id].json` - [Description]
[... list all ...]
```
