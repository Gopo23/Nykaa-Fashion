import os
import datetime
import pandas as pd
from sqlalchemy import create_engine
from google_play_scraper import Sort, reviews
from app_store_scraper import AppStore
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT
from dotenv import load_dotenv

load_dotenv()

# Database connection details (update via environment variables or default)
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "postgres")

# Target Apps
PLAY_STORE_APP_ID = "com.fsn.nykaa" # Main Nykaa app
APP_STORE_APP_NAME = "nykaa-fashion" 
APP_STORE_APP_ID = 1450533969 # Typical App store ID for Nykaa Fashion

MAX_REVIEWS_TOTAL = 5000
MAX_PER_PLATFORM = MAX_REVIEWS_TOTAL // 3
THREE_MONTHS_AGO = datetime.datetime.now() - datetime.timedelta(days=90)

def fetch_play_store_reviews():
    print(f"Fetching up to {MAX_PER_PLATFORM} reviews from Play Store...")
    try:
        result, continuation_token = reviews(
            PLAY_STORE_APP_ID,
            lang='en', # defaults to 'en'
            country='in', # defaults to 'us'
            sort=Sort.NEWEST, # defaults to Sort.NEWEST
            count=MAX_PER_PLATFORM # defaults to 100
        )
        
        valid_reviews = []
        for r in result:
            review_date = r['at']
            if review_date >= THREE_MONTHS_AGO:
                valid_reviews.append({
                    "review_id": f"play_{r['reviewId']}",
                    "source": "Play Store",
                    "review_text": r['content'],
                    "rating": r['score'],
                    "review_date": review_date,
                    "app_version": r.get('reviewCreatedVersion', 'Unknown')
                })
        print(f"Found {len(valid_reviews)} Play Store reviews from the last 3 months.")
        return valid_reviews
    except Exception as e:
        print(f"Error fetching Play Store reviews: {e}")
        return []

def fetch_app_store_reviews():
    print(f"Fetching up to {MAX_PER_PLATFORM} reviews from App Store...")
    try:
        nykaa = AppStore(country='in', app_name=APP_STORE_APP_NAME, app_id=APP_STORE_APP_ID)
        nykaa.review(how_many=MAX_PER_PLATFORM, after=THREE_MONTHS_AGO)
        
        valid_reviews = []
        for r in nykaa.reviews:
            valid_reviews.append({
                "review_id": f"app_{r['id']}",
                "source": "App Store",
                "review_text": r['review'],
                "rating": r['rating'],
                "review_date": r['date'],
                "app_version": r.get('version', 'Unknown')
            })
        print(f"Found {len(valid_reviews)} App Store reviews from the last 3 months.")
        return valid_reviews
    except Exception as e:
        print(f"Error fetching App Store reviews: {e}")
        return []

def fetch_youtube_comments():
    print(f"Fetching up to {MAX_PER_PLATFORM} reviews from YouTube...")
    try:
        downloader = YoutubeCommentDownloader()
        
        # Hardcoded YouTube haul videos for Nykaa Fashion
        video_urls = [
            "https://www.youtube.com/watch?v=yDzaN3xLwp0",
            "https://www.youtube.com/watch?v=ous9qVmohE4",
            "https://www.youtube.com/watch?v=M78d10Cb97s",
            "https://www.youtube.com/watch?v=l8Pv9-LJVrg",
            "https://www.youtube.com/watch?v=UXoqTkvBwsg"
        ]
        
        valid_reviews = []
        for url in video_urls:
            if len(valid_reviews) >= MAX_PER_PLATFORM:
                break
                
            comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_RECENT)
            for comment in comments:
                if len(valid_reviews) >= MAX_PER_PLATFORM:
                    break
                    
                # The time_parsed is a float timestamp
                if 'time_parsed' in comment and comment['time_parsed']:
                    comment_date = datetime.datetime.fromtimestamp(comment['time_parsed'])
                    if comment_date >= THREE_MONTHS_AGO:
                        valid_reviews.append({
                            "review_id": f"yt_{comment['cid']}",
                            "source": "YouTube",
                            "review_text": comment['text'],
                            "rating": None,
                            "review_date": comment_date,
                            "app_version": "Unknown"
                        })
                    else:
                        break # Videos are sorted by recent, we can break if too old
        
        print(f"Found {len(valid_reviews)} YouTube comments from the last 3 months.")
        return valid_reviews
    except Exception as e:
        print(f"Error fetching YouTube comments: {e}")
        return []

def main():
    print("Starting extraction...")
    all_reviews = []
    
    # 1. Fetch from Play Store
    play_reviews = fetch_play_store_reviews()
    all_reviews.extend(play_reviews)
    
    # 2. Fetch from App Store
    app_reviews = fetch_app_store_reviews()
    all_reviews.extend(app_reviews)
    
    # 3. YouTube placeholder
    yt_reviews = fetch_youtube_comments()
    all_reviews.extend(yt_reviews)
    
    # Cap at exactly 5000 if it exceeded
    if len(all_reviews) > MAX_REVIEWS_TOTAL:
        all_reviews = all_reviews[:MAX_REVIEWS_TOTAL]
    
    print(f"Total reviews collected within the last 3 months: {len(all_reviews)}")
    
    if len(all_reviews) == 0:
        print("No reviews found. Exiting.")
        return
        
    df = pd.DataFrame(all_reviews)
    
    # Always save to CSV
    csv_path = "nykaa_reviews_dataset.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved dataset to {csv_path}")
    
    # 4. Save to Database
    import urllib.parse
    safe_user = urllib.parse.quote_plus(DB_USER)
    safe_pass = urllib.parse.quote_plus(DB_PASS)
    engine_url = f"postgresql://{safe_user}:{safe_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    try:
        engine = create_engine(engine_url)
        
        print("Inserting records into PostgreSQL (table: nykaa_raw_reviews)...")
        # Append data. We only write columns that exist in the dataframe. 
        # ID, category, embedding, created_at will be handled by Postgres defaults/nulls
        df.to_sql('nykaa_raw_reviews', engine, if_exists='append', index=False)
        print("Insertion complete!")
        
    except Exception as e:
        print(f"Failed to connect or write to PostgreSQL: {e}")

if __name__ == "__main__":
    main()
