# Phase 1 PoC Insights Report

## Overview
Total reviews analyzed: 20
AI Model Used: Local Fallback (TF-IDF/Regex)

## 1. Classification Breakdown
- **Ambiguous/Other**: 7 reviews (35.0%)
- **Fit/Size**: 5 reviews (25.0%)
- **Price/Value**: 3 reviews (15.0%)
- **Delivery**: 2 reviews (10.0%)
- **Quality/Authenticity**: 2 reviews (10.0%)
- **Return Policy**: 1 reviews (5.0%)

## 2. Unsupervised Clustering Discoveries
The clustering algorithm grouped the feedback into themes independent of the categories.

### Cluster 0 (Size: 3)
Sample reviews from this cluster:
- "I really like the dress but the size chart is confusing. Not sure what to order." (Categorized as: *Fit/Size*)
- "Bhai fabric toh accha hai but smj nai aara size kaisa hoga idc lol" (Categorized as: *Fit/Size*)
- "Does anyone know if this is true to size?" (Categorized as: *Fit/Size*)

### Cluster 1 (Size: 13)
Sample reviews from this cluster:
- "The fabric quality looks cheap in real life compared to the video." (Categorized as: *Quality/Authenticity*)
- "It's okay." (Categorized as: *Ambiguous/Other*)
- "Will this look good for a Diwali party?" (Categorized as: *Ambiguous/Other*)

### Cluster 2 (Size: 2)
Sample reviews from this cluster:
- "Price is too high for this material. Call me at [PHONE] if price drops." (Categorized as: *Price/Value*)
- "Loved the dress but delivery took 2 weeks and the price was way too high for this fabric quality." (Categorized as: *Price/Value*)

### Cluster 3 (Size: 2)
Sample reviews from this cluster:
- "Delivery was way too slow. Took 15 days to arrive!" (Categorized as: *Delivery*)
- "Oh sure, the delivery was 'lightning fast' taking only 14 days. 🙄" (Categorized as: *Delivery*)

## 3. Notable Edge Cases Handled
- **PII Scrubbing**: Emails and phone numbers were successfully anonymized before processing.
- **Mixed Languages/Sarcasm**: Evaluated based on context rather than simple keyword matching (if using LLM).
