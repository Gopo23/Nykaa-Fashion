# System Architecture — AI-Powered Discovery Engine

This document outlines the architecture for the AI-powered discovery engine proposed for Nykaa Fashion. The system is designed to ingest, process, analyze, and visualize user feedback at scale from multiple sources to uncover hidden decision barriers between wishlisting and purchasing.

## 1. High-Level Architecture Overview

The system is divided into five core layers:
1. **Data Ingestion Layer**: Collects data from external platforms.
2. **Data Storage Layer**: Stores raw, processed, and vector data.
3. **AI & Processing Layer**: Cleans, translates, embeds, and analyzes the text.
4. **Insights & Serving Layer**: Exposes analyzed data via APIs.
5. **Visualization Layer**: Dashboards for product/growth teams to explore insights.

---

## 2. Component Details

### 2.1. Data Ingestion Layer
Responsible for continuous, automated data collection from publicly available sources.

*   **App Store Reviews**: Accessed via Apple App Store Connect API or custom scrapers (e.g., `app-store-scraper`).
*   **Play Store Reviews**: Accessed via Google Play Developer API or custom scrapers (e.g., `google-play-scraper`).
*   **YouTube Comments**: Accessed via YouTube Data API v4, focusing on haul videos, review videos, and Nykaa Fashion campaigns.
*   **Orchestration**: Apache Airflow or AWS Step Functions to schedule and manage data ingestion pipelines (e.g., daily or weekly syncs).

### 2.2. Data Storage Layer
A scalable storage solution to handle large volumes of unstructured and structured text using a unified relational database architecture.

*   **Unified Data Store**: PostgreSQL running via Docker to handle all data layers securely on-premise/locally.
*   **Raw & Structured Tables**: Storing raw JSON/CSV dumps of reviews as well as cleaned metadata (timestamps, ratings, platform, extracted categories).
*   **Vector Database**: PostgreSQL using the `pgvector` extension to store text embeddings natively for semantic search, clustering, and retrieval alongside the relational data.

### 2.3. AI & Processing Layer
The core brain of the discovery engine that transforms raw text into structured behavioral insights.

*   **Data Preprocessing Pipeline**:
    *   **PII Scrubbing**: Removes names, phone numbers, etc.
    *   **Translation**: Translates regional languages/Hinglish to English using models like Google Cloud Translation API or local models.
    *   **Spam Filtering**: Removes irrelevant comments or bot spam.
*   **LLM Processing Engine** (e.g., Groq qwen/qwen3.8-27b):
    *   **Classification**: Zero-shot or few-shot prompts to categorize feedback into predefined decision barriers (e.g., *Fit/Size, Price/Value, Quality/Authenticity, Delivery, Social Proof*).
    *   **Entity Extraction**: Identifies specific product categories (e.g., "Kurtas", "Sneakers") or brands mentioned in the feedback.
*   **Unsupervised Discovery Engine**:
    *   **Text Embedding**: Converts reviews into dense vectors using models like OpenAI `text-embedding-3-small`.
    *   **Clustering**: Uses algorithms like HDBSCAN or K-Means on the embeddings to discover *new, unexpected* user problems that weren't predefined (e.g., a sudden cluster of complaints about a specific return policy change).

### 2.4. Insights & Serving Layer
*   **Aggregation Engine**: SQL/Python jobs that quantify the frequency of specific barriers over time (e.g., "What % of complaints this week were about sizing?").
*   **REST/GraphQL API**: A backend service (FastAPI or Node.js) that serves processed insights, sentiment trends, and raw text examples to the frontend.
*   **Automated Summarization**: An LLM agent that runs weekly to generate a natural language summary of top emerging barriers and opportunities for the growth team.

### 2.5. Visualization Layer
Where Nykaa Fashion Product and Growth teams interact with the data.

*   **Internal Dashboard**: Built with Streamlit, Retool, or a custom React application.
*   **Features**:
    *   **Trend Tracking**: Line charts showing the volume of specific barriers over time.
    *   **Cluster Visualization**: A 2D scatter plot (using UMAP/t-SNE) of user feedback clusters to visually explore themes.
    *   **Drill-Down**: The ability to click on a barrier (e.g., "Material Quality") and read the raw reviews driving that insight.
    *   **Segment Comparison**: Filters to compare problems between Android vs. iOS users, or high-rated vs. low-rated reviews.

---

## 3. Technology Stack Recommendation

| Component | Recommended Technology |
| :--- | :--- |
| **Infrastructure** | Docker / Docker Compose |
| **Orchestration** | Apache Airflow |
| **Unified Data Store**| PostgreSQL |
| **Vector Database** | PostgreSQL (`pgvector` extension) |
| **AI / LLMs** | Groq (qwen/qwen3.8-27b) and BAAI/bge-base-en-v1.5 (Embeddings) |
| **Backend API** | Python (FastAPI) |
| **Frontend/Dashboard**| Streamlit (for rapid prototyping) / React (for production) |

---

## 4. Workflow Example

1. **Ingest**: Airflow triggers a script that pulls 5,000 new YouTube comments from Nykaa Fashion haul videos using APIs/Scrapers.
2. **Clean**: The script drops emojis, translates Hindi to English, and saves them to a raw PostgreSQL table.
3. **Embed & Analyze**: The text is sent to the Groq Qwen LLM. The LLM tags a comment: `Intent: High`, `Barrier: Uncertain about material`. The text is also embedded using BAAI's embedding model.
4. **Store**: The tag, metadata, and the embedding array are upserted into the structured PostgreSQL tables (using `pgvector`).
5. **Discover**: An analyst opens the Streamlit dashboard, clicks on the "Uncertain about material" tag, reads the clustered comments, and realizes users lack close-up texture photos for a specific ethnic wear brand.
6. **Action**: The growth team proposes adding video reviews or close-up fabric shots to product pages to unblock this specific intent.
