import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import urllib.parse
from datetime import datetime

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

def fetch_instagram_data():
    """
    Mock function to represent fetching Instagram Comments.
    In a real scenario, this would use the Instagram Graph API
    (e.g., fetching comments from a recent Nykaa Fashion post).
    """
    print("Connecting to Instagram Graph API... (Mock)")
    
    # Mock data simulating Instagram comments
    mock_comments = [
        {
            "review_id": "ig_1001",
            "source": "Instagram",
            "review_text": "Love this top! Saved it to my wishlist but waiting for a price drop 😢",
            "rating": None,
            "review_date": datetime.now(),
            "app_version": None
        },
        {
            "review_id": "ig_1002",
            "source": "Instagram",
            "review_text": "I tried adding this to my cart from my wishlist but it says unavailable in my size (M). Please restock!",
            "rating": None,
            "review_date": datetime.now(),
            "app_version": None
        }
    ]
    
    return mock_comments

def save_to_db(comments):
    """Saves the raw comments to the nykaa_raw_reviews table."""
    with engine.connect() as conn:
        for comment in comments:
            # Check if exists
            query = text("SELECT 1 FROM nykaa_raw_reviews WHERE review_id = :review_id")
            result = conn.execute(query, {"review_id": comment["review_id"]}).fetchone()
            
            if not result:
                insert_query = text("""
                    INSERT INTO nykaa_raw_reviews (review_id, source, review_text, rating, review_date, app_version)
                    VALUES (:review_id, :source, :review_text, :rating, :review_date, :app_version)
                """)
                conn.execute(insert_query, comment)
                conn.commit()
                print(f"Inserted Instagram comment {comment['review_id']} into database.")
            else:
                print(f"Instagram comment {comment['review_id']} already exists, skipping.")

def main():
    print("Starting Instagram Data Ingestion...")
    comments = fetch_instagram_data()
    save_to_db(comments)
    print("Instagram Data Ingestion Complete.")

if __name__ == "__main__":
    main()
