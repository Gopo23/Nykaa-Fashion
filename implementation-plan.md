# Phase-Wise Implementation Plan — AI-Powered Discovery Engine

This document outlines the strategic, phase-wise implementation plan to build the AI-Powered Discovery Engine for Nykaa Fashion, as defined in the `problemstatement.md` and `architecture.md`.

The plan is designed to deliver value incrementally, starting with a Proof of Concept (PoC) to validate the core AI capabilities before scaling into a fully automated production system.

---

## Phase 1: Proof of Concept & Feasibility Validation (Weeks 1–3)
**Objective:** Validate that LLMs can accurately identify decision barriers from unstructured reviews and that the data holds actionable insights.

*   **Step 1.1: Automated Data Extraction (Completed):** Built and executed a Python script (`fetch_real_reviews.py`) to automatically extract a static sample of recent reviews (last 3 months, capped at 5,000) from App Store, Play Store, and YouTube comments on popular haul videos. The dataset is saved locally as `nykaa_reviews_dataset.csv`.
*   **Step 1.2: Basic Preprocessing:** Run basic Python scripts to clean text and remove PII.
*   **Step 1.3: Prompt Engineering & Zero-Shot Classification:** Use Groq's qwen/qwen3.8-27b model to categorize the sample data into predefined barriers (e.g., *Fit, Quality, Price, Delivery*).
*   **Step 1.4: Initial Discovery Clustering:** Generate embeddings for the sample data and run K-Means/HDBSCAN clustering to uncover unexpected unmet needs.
*   **Deliverable:** A static report (PDF/Presentation) showcasing 3–5 key insights regarding why users are not purchasing wishlisted items.

---

## Phase 2: Data Ingestion & Storage Foundation (Weeks 4–6)
**Objective:** Automate the collection of feedback and establish the foundational data architecture.

*   **Step 2.1: Infrastructure Setup:** Ensure your local Docker environment is running, and configure the existing PostgreSQL database to act as the primary data warehouse (installing the `pgvector` extension if needed).
*   **Step 2.2: API & Scraper Development (Completed):** Built Python-based ingestion scripts for:
    *   App Store (via `app-store-scraper`)
    *   Google Play Store (via `google-play-scraper`)
    *   YouTube Comments (via `youtube-comment-downloader`)
*   **Step 2.3: Orchestration:** Set up a scheduled task or Apache Airflow to run these ingestion jobs on a regular cadence, pushing data directly into the PostgreSQL `nykaa_raw_reviews` table.
*   **Deliverable:** A local Dockerized PostgreSQL database continuously ingesting raw user feedback.

---

## Phase 3: AI Engine & Processing Pipeline (Weeks 7–10)
**Objective:** Build the core intelligence layer to process, translate, embed, and categorize incoming data at scale.

**Rule:** Only filter reviews from raw review data which have similar words like 'Wishlist', 'Add to Cart', 'Buy Later', etc. so the data showing up on the frontend is related and creates 5 major themes affecting 'Wishlist → Purchase Conversion' for Nykaa fashion.

*   **Step 3.1: Translation & Cleaning Pipeline:** Implement automated translation (e.g., Hinglish/Hindi to English) and robust spam filtering.
*   **Step 3.2: Automated Classification:** Deploy the LLM classification prompts developed in Phase 1 into the Airflow pipeline to tag every new review automatically.
*   **Step 3.3: Entity Extraction:** Configure the AI to identify specific product categories (e.g., "Kurtas," "Heels") and brands mentioned in the text.
*   **Step 3.4: Vectorization & Storage:** Generate text embeddings (`text-embedding-3-small`) for all feedback and push them to a Vector Database (e.g., Pinecone or pgvector).
*   **Deliverable:** A continuous, automated data flow where raw text is transformed into structured, searchable, and categorized behavioral data stored in the Data Warehouse.

---

## Phase 4: Analytics, Dashboard, & Visualization (Weeks 11–13)
**Objective:** Make the insights accessible and actionable for the Nykaa Fashion Product and Growth teams.

*   **Step 4.1: API Development:** Develop a REST/GraphQL API using FastAPI to serve aggregated metrics and vector searches to the frontend.
*   **Step 4.2: Dashboard MVP:** Build an internal Streamlit or React web application with:
    *   Time-series charts for tracking barrier trends (e.g., "Size complaints over time").
    *   A visual cluster map for unsupervised discovery.
    *   A drill-down interface to read raw user quotes linked to specific categories.
*   **Step 4.3: User Testing:** Roll out the dashboard MVP to a select group of Product Managers and UX Researchers for feedback.
*   **Deliverable:** An interactive internal dashboard serving real-time insights on user decision barriers.

---

## Phase 5: Refinement, Integration, & Scaling (Weeks 14+)
**Objective:** Scale the system, refine the AI models, and integrate insights directly into product roadmaps.

*   **Step 5.1: Automated Reporting:** Develop an LLM agent that synthesizes weekly data into a brief "Top Emerging Barriers" summary emailed to stakeholders.
*   **Step 5.2: Expanded Data Sources:** Integrate additional unstructured feedback channels, such as Instagram comments, Twitter mentions, and customer support chat transcripts (Zendesk).
*   **Step 5.3: Model Fine-Tuning:** If necessary, transition from zero-shot LLM prompts to a fine-tuned, smaller, and cheaper model (e.g., fine-tuned Llama 3) to reduce processing costs.
*   **Deliverable:** A highly scalable, cost-efficient, production-grade AI Discovery Engine that directly informs the Nykaa Fashion product roadmap.
