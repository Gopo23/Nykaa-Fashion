import schedule
import time
import fetch_real_reviews
import fetch_zendesk_tickets
import fetch_instagram_comments
import process_reviews
import weekly_report_agent
import datetime
from dotenv import load_dotenv

load_dotenv()

def daily_job():
    print(f"[{datetime.datetime.now()}] Starting scheduled daily data ingestion...")
    fetch_real_reviews.main()
    fetch_zendesk_tickets.main()
    fetch_instagram_comments.main()
    print(f"[{datetime.datetime.now()}] Finished scheduled daily data ingestion.")
    
    print(f"[{datetime.datetime.now()}] Starting scheduled review processing...")
    process_reviews.main()
    print(f"[{datetime.datetime.now()}] Finished scheduled review processing.")

def weekly_job():
    print(f"[{datetime.datetime.now()}] Starting scheduled weekly reporting...")
    weekly_report_agent.main()
    print(f"[{datetime.datetime.now()}] Finished scheduled weekly reporting.")

if __name__ == "__main__":
    print(f"[{datetime.datetime.now()}] Initializing review extraction scheduler...")
    
    # Run the daily job immediately once on startup
    daily_job()
    
    # Schedule the daily job to run every day at midnight
    schedule.every().day.at("00:00").do(daily_job)
    
    # Schedule the weekly report to run every Monday at 8 AM
    schedule.every().monday.at("08:00").do(weekly_job)
    
    print("Scheduler running. Press Ctrl+C to exit.")
    
    while True:
        schedule.run_pending()
        time.sleep(60) # check every minute
