# Edge Cases and Corner Scenarios

This document outlines potential edge cases, anomalies, and corner scenarios that the AI-Powered Discovery Engine must account for. Addressing these scenarios ensures the integrity of the data pipeline and the accuracy of the insights delivered to the Nykaa Fashion product team.

## 1. Data Quality and Ingestion Edge Cases

*   **Multilingual "Frankenstein" Text:** A single review contains a mix of English, Hindi, regional slang, and abbreviations (e.g., *"Bhai fabric toh accha hai but smj nai aara size kaisa hoga idc lol"*).
    *   *Mitigation:* Use robust, multilingual LLMs for preprocessing and translation before semantic clustering.
*   **Sarcasm and Double Negatives:** Feedback such as *"Oh sure, the delivery was 'lightning fast' taking only 14 days."*
    *   *Mitigation:* Standard sentiment analysis often fails here; rely on contextual LLM processing that can detect sarcastic tone and tag it as a "Delivery Delay" barrier.
*   **Vague or Non-Specific Feedback:** Reviews like *"Didn't like it,"* *"Bad,"* or *"Nice."*
    *   *Mitigation:* Create a specific `Ambiguous/No-Data` classification tag to filter these out before embedding, so they don't skew the clustering models.
*   **Coordinated Spam / Fake Reviews:** A sudden influx of bot-generated negative reviews (e.g., competitors) or fake positive reviews (e.g., paid campaigns).
    *   *Mitigation:* Implement anomaly detection on ingestion (e.g., flagging bursts of reviews with similar timestamps and text similarity).
*   **API Rate Limiting & Changes:** Third-party APIs (Google Play, App Store, YouTube) throttle requests or change their response JSON schemas unexpectedly.
    *   *Mitigation:* Implement exponential backoff in Airflow operators, set up schema validation checks before ingestion, and establish alert triggers for pipeline failures.

## 2. AI Processing and Categorization Edge Cases

*   **Multi-Intent / Conflicting Reviews:** A user lists multiple barriers in one comment: *"The dress is beautiful, but the size chart is completely wrong, it's way overpriced, and customer support ignored me."*
    *   *Mitigation:* The LLM should be instructed to output multiple tags (e.g., `[Size/Fit, Price, Customer Support]`) rather than forcing a single dominant category.
*   **Contextual Ambiguity (Entity Confusion):** A user writes, *"I bought the MAC."* On a fashion and beauty platform, this likely means MAC Cosmetics, but a generic NLP model might classify it as electronics.
    *   *Mitigation:* Provide the LLM or entity extractor with a Nykaa-specific dictionary/context prompt.
*   **LLM Hallucinations:** The LLM categorizes a review under a barrier that doesn't exist in the predefined schema, or misinterprets a complex sentence.
    *   *Mitigation:* Use strict JSON-mode outputs or constrained generation (like Instructor/Pydantic validation) to force the LLM to pick only from an approved list of enums.
*   **PII Leakage in Edge Formats:** Users post their phone numbers or home addresses in highly unusual formats (e.g., *"call me at 9 eight 7 six..."*) that bypass standard regex PII scrubbers.
    *   *Mitigation:* Implement a secondary LLM-based PII detection step before pushing raw text to the Vector Database.

## 3. Storage and Infrastructure Edge Cases

*   **Vector Embedding Model Updates:** The underlying embedding provider (e.g., OpenAI) updates their model, changing the dimensionality of the vectors (e.g., from 1536 to 3072 dims).
    *   *Mitigation:* Version control the vector database indices. If the model changes, trigger a full re-embedding backfill job on historical data rather than mixing dimensions.
*   **Database Overload from Viral Outages:** The Nykaa Fashion app crashes during a massive sale, resulting in 50x the normal volume of App Store reviews in one hour.
    *   *Mitigation:* Auto-scaling infrastructure for the LLM processing queue (e.g., using Celery/Redis) so the Airflow pipeline doesn't crash, but instead slowly processes the backlog.

## 4. Analytics and Visualization Edge Cases

*   **The "Everything is Bad" Mega-Cluster:** Unsupervised clustering (HDBSCAN/K-Means) groups 60% of all data into one giant, unhelpful "Miscellaneous" bubble because the embeddings are too semantically similar.
    *   *Mitigation:* Apply hierarchical clustering to recursively break down massive clusters into smaller, more specific sub-themes.
*   **Silent Pipeline Failures:** The data ingestion fails silently, and the dashboard continues to display data from three weeks ago, leading product managers to make decisions on stale data.
    *   *Mitigation:* Embed a prominent "Last Updated" timestamp on the Streamlit/React dashboard and trigger Slack alerts to the data engineering team if no new records are ingested within 48 hours.
*   **Over-Indexing on Loud Minorities:** A specific, niche problem (e.g., a bug affecting only iOS 14 users) generates highly emotional, lengthy reviews that the AI flags as a massive opportunity, overshadowing a quieter but more financially impactful sizing issue.
    *   *Mitigation:* Weigh the insights dashboard not just by the *volume* or *sentiment* of the feedback, but by cross-referencing the issue with actual purchase/wishlist data if available (e.g., mapping user IDs where possible).
