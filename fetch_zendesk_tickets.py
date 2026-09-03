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

def fetch_zendesk_data():
    """
    Mock function to represent fetching Zendesk Chat Transcripts.
    In a real scenario, this would use the Zendesk Support API
    (e.g., using requests to https://{subdomain}.zendesk.com/api/v2/tickets.json)
    """
    print("Connecting to Zendesk API... (Mock)")
    
    # Mock data simulating a Zendesk ticket about a wishlist
    mock_tickets = [
        {
            "review_id": "zd_1001",
            "source": "Zendesk",
            "review_text": "Hi, I added a dress to my wishlist yesterday but today it says out of stock. When will it be back?",
            "rating": None,
            "review_date": datetime.now(),
            "app_version": "Web"
        },
        {
            "review_id": "zd_1002",
            "source": "Zendesk",
            "review_text": "I can't move items from my wishlist to my cart, the app keeps crashing.",
            "rating": None,
            "review_date": datetime.now(),
            "app_version": "iOS 2.1.0"
        }
    ]
    
    return mock_tickets

def save_to_db(tickets):
    """Saves the raw tickets to the nykaa_raw_reviews table."""
    with engine.connect() as conn:
        for ticket in tickets:
            # Check if exists
            query = text("SELECT 1 FROM nykaa_raw_reviews WHERE review_id = :review_id")
            result = conn.execute(query, {"review_id": ticket["review_id"]}).fetchone()
            
            if not result:
                insert_query = text("""
                    INSERT INTO nykaa_raw_reviews (review_id, source, review_text, rating, review_date, app_version)
                    VALUES (:review_id, :source, :review_text, :rating, :review_date, :app_version)
                """)
                conn.execute(insert_query, ticket)
                conn.commit()
                print(f"Inserted Zendesk ticket {ticket['review_id']} into database.")
            else:
                print(f"Zendesk ticket {ticket['review_id']} already exists, skipping.")

def main():
    print("Starting Zendesk Data Ingestion...")
    tickets = fetch_zendesk_data()
    save_to_db(tickets)
    print("Zendesk Data Ingestion Complete.")

if __name__ == "__main__":
    main()
