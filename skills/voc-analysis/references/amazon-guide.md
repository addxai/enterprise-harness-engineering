# Amazon ASIN Search Guide

Amazon Reviews Scrapers require ASIN (Amazon Standard Identification Number) — a 10-character alphanumeric product ID.

---

## Finding ASINs

### Method 1: Extract from URL (Fastest)

```
https://www.amazon.com/dp/<YOUR_ASIN> → ASIN: <YOUR_ASIN>
https://amazon.com/Product-Name/dp/<YOUR_ASIN>/ref=... → ASIN: <YOUR_ASIN>
```

Look for `/dp/` or `/product/` in the URL, copy the 10-character code after it.

### Method 2: Apify Product Search (Recommended for bulk)

1. Search Apify Store: `mcp_apify_search-actors` keywords: "amazon product search"
2. Use: `junglee/free-amazon-product-scraper` or similar
3. Input:
   ```json
   {
     "categoryUrls": [{"url": "https://amazon.com/s?k=product+category"}],
     "maxItemsPerStartUrl": 20
   }
   ```
4. Output: JSON with ASINs, prices, ratings for 20 products
5. Use ASINs with review scraper

**Why this is good:**
- Automated bulk discovery (20-50 products at once)
- Auto-finds competitors in category
- Returns structured data (ASIN + price + rating)
- Repeatable

### Method 3: Web Search

```
"[product name]" site:amazon.com
```

Open the product page, extract ASIN from URL.

---

## Using ASINs with Review Scrapers

### junglee/amazon-reviews-scraper
```json
{
  "asin": ["<YOUR_ASIN>", "<COMPETITOR_ASIN_1>"],
  "maxReviews": 100,
  "country": "US"
}
```

### axesso_data/amazon-reviews-scraper
```json
{
  "productUrls": [
    "https://amazon.com/dp/<YOUR_ASIN>"
  ],
  "maxReviews": 100
}
```

Always check the actor's input schema with `mcp_apify_fetch-actor-details` — formats vary between actors.

---

## Review Scraping Strategy

### Layer 1 — Own Product (Direct)
```json
{"asin": ["<YOUR_ASIN>"], "maxReviews": 100, "country": "US", "sortBy": "recent"}
```

### Layer 3 — Competitor Analysis
```json
{
  "asin": ["<COMPETITOR_ASIN_1>", "<COMPETITOR_ASIN_2>", "<COMPETITOR_ASIN_3>"],
  "maxReviews": 100,
  "country": "US",
  "sortBy": "helpful"
}
```

### Review Filtering Strategy
- **Recent feedback**: `sortBy: "recent"` — last 3-6 months
- **Critical issues**: Focus on 1-2 star reviews
- **Success patterns**: Focus on 5 star reviews
- **Helpful reviews**: `sortBy: "helpful"` — most verified purchase insights

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Invalid ASIN | Verify 10-character alphanumeric |
| Region mismatch | Specify correct country code (US/UK/DE/JP) |
| No reviews | Product may be too new |
| Different regions | Same product has different ASINs on .com vs .co.uk |

---

## ASIN Checklist

- [ ] Identified own product on Amazon
- [ ] Extracted own product ASIN from URL
- [ ] Found 3-5 competitor products
- [ ] Extracted all competitor ASINs
- [ ] Verified ASINs are 10-character alphanumeric
- [ ] Chose appropriate Amazon actor
- [ ] Checked actor's required input format
- [ ] Set maxReviews (recommend 100+ per product)
- [ ] Specified country code if <region>
