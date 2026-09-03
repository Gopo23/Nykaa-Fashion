-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table to store raw user reviews
CREATE TABLE IF NOT EXISTS nykaa_raw_reviews (
    id SERIAL PRIMARY KEY,
    review_id VARCHAR(255) UNIQUE NOT NULL, -- Store platform specific ID
    source VARCHAR(50) NOT NULL, -- 'App Store', 'Play Store', 'YouTube'
    review_text TEXT NOT NULL,
    rating INTEGER, -- Nullable for YouTube
    review_date TIMESTAMP WITH TIME ZONE,
    app_version VARCHAR(50), -- Specific to app stores
    -- Vector embedding column (dimension 768 is typical for standard Gemini embeddings, adjust if using a different model)
    embedding vector(768), 
    category VARCHAR(255), -- AI categorized intent/barrier
    -- Phase 3 AI Processing Columns
    clean_text TEXT,
    entities JSONB,
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for semantic search
CREATE INDEX IF NOT EXISTS nykaa_raw_reviews_embedding_idx 
ON nykaa_raw_reviews USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
