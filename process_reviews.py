import os
import json
import urllib.parse
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
import warnings
import time

# Suppress HuggingFace/Torch warnings for cleaner output
warnings.filterwarnings("ignore")

load_dotenv()

# Database setup
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "postgres")

safe_user = urllib.parse.quote_plus(DB_USER)
safe_pass = urllib.parse.quote_plus(DB_PASS)
engine_url = f"postgresql://{safe_user}:{safe_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(engine_url)

# Groq setup
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env")

client = Groq(api_key=GROQ_API_KEY)

# Embedding Model Setup
print("Loading BGE embedding model (this might take a moment)...")
embedding_model = SentenceTransformer('BAAI/bge-base-en-v1.5')
print("Model loaded successfully.")

def process_single_review(review_text):
    prompt = f"""
Analyze the following user review for Nykaa Fashion:
"{review_text}"

First, determine if the review explicitly or implicitly mentions concepts like "Wishlist", "Add to Cart", "Buy Later", or barriers to moving from a wishlist/cart to a final purchase. 
If the review does NOT relate to these themes, return a JSON object with "clean_text" set to "IRRELEVANT" and nothing else.

If it IS related to wishlist/cart conversion, return a JSON object with EXACTLY these keys:
- "clean_text": The English translation and cleaned version of the text (remove spam/gibberish, fix typos). If it's just spam, write "SPAM".
- "category": The primary barrier affecting the 'Wishlist → Purchase' conversion. Choose ONE from: 
  ["Price / Better Offers Elsewhere", "Size & Fit Uncertainty", "Out of Stock / Unavailability", "Delivery / Shipping Costs", "App Usability / Glitches"].
- "entities": A JSON object containing:
    - "brands": List of brands mentioned (e.g., ["Biba", "Puma"]).
    - "categories": List of product categories mentioned (e.g., ["Kurta", "Heels", "Dresses"]).
"""
    try:
        response = client.chat.completions.create(
            model='qwen/qwen3.8-27b',
            messages=[
                {"role": "system", "content": "You are a helpful data analyst. Always respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content.strip()
        result = json.loads(response_text)
        return result
    except Exception as e:
        print(f"Error processing review with Groq: {e}")
        return None

def main():
    print("Starting AI review processing pipeline...")
    
    with engine.connect() as conn:
        # Fetch unprocessed reviews
        query = text("SELECT id, review_text FROM nykaa_raw_reviews WHERE is_processed = FALSE LIMIT 100")
        result = conn.execute(query)
        rows = result.fetchall()
        
        if not rows:
            print("No unprocessed reviews found.")
            return

        print(f"Found {len(rows)} reviews to process.")
        
        processed_count = 0
        for row in rows:
            row_id, review_text = row.id, row.review_text
            
            # 1. LLM Processing via Gemini
            ai_result = process_single_review(review_text)
            
            if not ai_result:
                print(f"Failed to process review {row_id}, skipping...")
                continue
                
            clean_text_response = ai_result.get("clean_text", "")
            if clean_text_response in ["SPAM", "IRRELEVANT"]:
                # Mark as processed but ignore SPAM/IRRELEVANT
                update_query = text("""
                    UPDATE nykaa_raw_reviews 
                    SET is_processed = TRUE, category = :status, clean_text = :status
                    WHERE id = :id
                """)
                conn.execute(update_query, {"id": row_id, "status": clean_text_response.capitalize()})
                conn.commit()
                continue
            
            clean_text = ai_result.get("clean_text", review_text)
            category = ai_result.get("category", "Other")
            entities = json.dumps(ai_result.get("entities", {"brands": [], "categories": []}))
            
            # 2. Embedding Generation via BGE
            # BGE model encodes text into 768-dimensional float32 arrays
            vector = embedding_model.encode(clean_text, normalize_embeddings=True)
            # pgvector expects a string representation of the array e.g., "[0.1, 0.2, ...]"
            vector_str = f"[{','.join(map(str, vector.tolist()))}]"
            
            # 3. Database Update
            update_query = text("""
                UPDATE nykaa_raw_reviews 
                SET is_processed = TRUE, 
                    clean_text = :clean_text,
                    category = :category,
                    entities = :entities,
                    embedding = :embedding
                WHERE id = :id
            """)
            conn.execute(update_query, {
                "clean_text": clean_text,
                "category": category,
                "entities": entities,
                "embedding": vector_str,
                "id": row_id
            })
            conn.commit()
            processed_count += 1
            
            # Small sleep to respect rate limits if any
            time.sleep(1)
            
        print(f"Successfully processed {processed_count} reviews.")

if __name__ == "__main__":
    main()
