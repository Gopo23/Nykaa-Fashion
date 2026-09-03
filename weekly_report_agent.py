import os
import json
import urllib.parse
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from groq import Groq
import smtplib
from email.message import EmailMessage

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

def fetch_weekly_data():
    """Fetches relevant reviews from the last 7 days."""
    seven_days_ago = datetime.now() - timedelta(days=7)
    with engine.connect() as conn:
        query = text("""
            SELECT category, clean_text 
            FROM nykaa_raw_reviews 
            WHERE is_processed = TRUE 
              AND category NOT IN ('Irrelevant', 'Spam')
              AND review_date >= :date
        """)
        result = conn.execute(query, {"date": seven_days_ago})
        rows = result.fetchall()
        
    # If the database doesn't have dates populated properly for tests, fallback to fetch everything
    if not rows:
        with engine.connect() as conn:
            query = text("""
                SELECT category, clean_text 
                FROM nykaa_raw_reviews 
                WHERE is_processed = TRUE 
                  AND category NOT IN ('Irrelevant', 'Spam')
            """)
            result = conn.execute(query)
            rows = result.fetchall()
    
    return rows

def generate_summary(reviews):
    """Uses Groq Qwen to synthesize the raw text into a summary."""
    if not reviews:
        return "No relevant reviews found this week."

    # Prepare data for LLM
    text_data = "\n".join([f"- [{row.category}] {row.clean_text}" for row in reviews[:50]]) # Limit to 50 for prompt context
    
    prompt = f"""
    You are a data analyst for Nykaa Fashion. 
    Analyze the following recent user reviews detailing why they abandoned their wishlist or cart:
    
    {text_data}
    
    Generate a brief, executive "Top Emerging Barriers" summary. 
    Format it in Markdown with bullet points, highlighting the most critical issues blocking 'Wishlist to Purchase' conversion.
    Include a short 'Recommended Action' section at the end.
    """
    
    try:
        response = client.chat.completions.create(
            model='qwen/qwen3.8-27b',
            messages=[
                {"role": "system", "content": "You are a concise and insightful data analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Error generating summary."

def save_and_email_report(report_md):
    """Saves the report locally and demonstrates email sending logic."""
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    
    filename = f"reports/weekly_summary_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Report saved to {filename}")
    
    # Mock Email Sending
    print("\n--- Mock Email Dispatch ---")
    print("To: stakeholders@nykaafashion.com")
    print("Subject: Weekly Insights: Wishlist to Purchase Barriers")
    print("Body:\n")
    print(report_md)
    print("\n---------------------------\n")
    print("Note: To send real emails, uncomment and configure the smtplib code in this script.")
    
    # Actual SMTP Logic (Commented out)
    """
    msg = EmailMessage()
    msg.set_content(report_md)
    msg['Subject'] = 'Weekly Insights: Wishlist to Purchase Barriers'
    msg['From'] = 'ai-insights@nykaafashion.com'
    msg['To'] = 'stakeholders@nykaafashion.com'

    # Need SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS from env
    try:
        server = smtplib.SMTP_SSL(os.environ.get("SMTP_SERVER"), int(os.environ.get("SMTP_PORT", 465)))
        server.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
        server.send_message(msg)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
    """

def main():
    print("Generating Weekly Report...")
    reviews = fetch_weekly_data()
    print(f"Found {len(reviews)} relevant reviews to summarize.")
    summary = generate_summary(reviews)
    save_and_email_report(summary)

if __name__ == "__main__":
    main()
