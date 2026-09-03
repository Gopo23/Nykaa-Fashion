import os
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

import json
import redis
import hashlib
from functools import wraps


load_dotenv()

app = FastAPI(title="Nykaa Fashion AI Discovery Engine API - Real Data")

# Database connection settings
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password")
DB_NAME = os.environ.get("DB_NAME", "postgres")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
except Exception:
    redis_client = None

def cache_response(ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not redis_client:
                return func(*args, **kwargs)
                
            # Filter out any non-serializable arguments (FastAPI passes things safely usually here)
            key_data = {"func": func.__name__, "args": args, "kwargs": kwargs}
            key_str = json.dumps(key_data, sort_keys=True, default=str)
            hashed_key = hashlib.md5(key_str.encode('utf-8')).hexdigest()
            cache_key = f"cache:{func.__name__}:{hashed_key}"
            
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
                
            result = func(*args, **kwargs)
            try:
                redis_client.setex(cache_key, ttl, json.dumps(result))
            except Exception:
                pass
            return result
        return wrapper
    return decorator


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            dbname=DB_NAME,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def build_where_clause(days: int, source: str = "All", category: str = "All"):
    """Helper to build dynamic SQL WHERE clauses based on frontend filters."""
    where = "WHERE is_processed = TRUE AND category NOT IN ('Irrelevant', 'Spam') "
    params = []
    
    # In PostgreSQL, we can use NOW() - INTERVAL
    where += "AND review_date >= NOW() - INTERVAL '%s days' "
    params.append(int(days))
    
    if source and source != "All":
        where += "AND source = %s "
        params.append(source)
        
    if category and category != "All Categories":
        where += "AND category = %s "
        params.append(category)
        
    return where, params

# --- Endpoints for Real Data Dashboard ---

@app.get("/api/v2/kpis")
@cache_response(ttl=300)
def get_v2_kpis(days: int = Query(30), source: str = Query("All"), category: str = Query("All Categories")):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        where_clause, params = build_where_clause(days, source, category)
        
        # Total Relevant Reviews (Proxy for high intent lost)
        cur.execute(f"SELECT COUNT(*) as total FROM nykaa_raw_reviews {where_clause}", tuple(params))
        total_reviews = cur.fetchone()['total']
        
        # Largest Barrier
        cur.execute(f"""
            SELECT category, COUNT(*) as count 
            FROM nykaa_raw_reviews 
            {where_clause}
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 1
        """, tuple(params))
        top_barrier_row = cur.fetchone()
        top_barrier = top_barrier_row['category'] if top_barrier_row else "N/A"
        
        # Calculate Trend (Compare to previous period)
        prev_where_clause, prev_params = build_where_clause(days * 2, source, category)
        # To get ONLY the previous period, we add an upper bound
        prev_where_clause += "AND review_date < NOW() - INTERVAL '%s days'"
        prev_params.append(int(days))
        
        cur.execute(f"SELECT COUNT(*) as prev_total FROM nykaa_raw_reviews {prev_where_clause}", tuple(prev_params))
        prev_total = cur.fetchone()['prev_total']
        
        if prev_total > 0:
            trend_val = ((total_reviews - prev_total) / prev_total) * 100
            trend = f"Up {trend_val:.1f}%" if trend_val > 0 else f"Down {abs(trend_val):.1f}%"
        else:
            trend = "Stable"
            
        return {
            "high_intent_users": total_reviews,
            "largest_barrier": top_barrier,
            "trend_30d": trend
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/v2/trends")
@cache_response(ttl=300)
def get_v2_trends(days: int = Query(30), source: str = Query("All"), category: str = Query("All Categories")):
    """Returns complaint volume trend over time."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        where_clause, params = build_where_clause(days, source, category)
        
        # Group by day
        query = f"""
            SELECT DATE(review_date) as date, COUNT(*) as complaint_volume
            FROM nykaa_raw_reviews
            {where_clause}
            GROUP BY DATE(review_date)
            ORDER BY date ASC
        """
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        
        results = []
        for row in rows:
            if row['date']:
                results.append({
                    "date": row['date'].strftime("%Y-%m-%d"),
                    "complaint_volume": row['complaint_volume']
                })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/v2/barriers")
@cache_response(ttl=300)
def get_v2_barriers(days: int = Query(30), source: str = Query("All"), category: str = Query("All Categories")):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        where_clause, params = build_where_clause(days, source, category)
        
        # We use frequency as "Users Affected" and a proxy for "Purchase Impact"
        query = f"""
            SELECT 
                category as barrier,
                COUNT(*) as users_affected,
                ROUND(AVG(COALESCE(rating, 3)), 2) as avg_rating
            FROM nykaa_raw_reviews
            {where_clause}
            GROUP BY category
            ORDER BY users_affected DESC
        """
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        
        # Calculate impact logic: Higher frequency + lower rating = higher impact
        for row in rows:
            # Simple heuristic: Impact = Users * (5 - Avg Rating)
            # If rating is low (1), it multiplies users by 4. If high (4), multiplies by 1.
            row['purchase_impact'] = int(row['users_affected'] * (5.0 - float(row['avg_rating'])))
            row['priority'] = "P0" if row['purchase_impact'] > 50 else ("P1" if row['purchase_impact'] > 20 else "P2")
            
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/v2/segments")
@cache_response(ttl=300)
def get_v2_segments(days: int = Query(30), source: str = Query("All"), category: str = Query("All Categories")):
    """Instead of demographics (which we don't have), segment by Data Source."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        where_clause, params = build_where_clause(days, source, category)
        
        query = f"""
            SELECT 
                source as segment,
                category as top_barrier,
                COUNT(*) as volume
            FROM nykaa_raw_reviews
            {where_clause}
            GROUP BY source, category
        """
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        
        # Group to find max barrier per source
        source_barriers = {}
        for r in rows:
            seg = r['segment']
            if seg not in source_barriers or r['volume'] > source_barriers[seg]['volume']:
                source_barriers[seg] = r
                
        return {"source": list(source_barriers.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/v2/insights")
@cache_response(ttl=300)
def get_v2_insights(days: int = Query(30), source: str = Query("All"), category: str = Query("All Categories")):
    """Generates real-time AI insights using Groq based on the filtered data."""
    if not client:
        return [{"barrier": "API Key Missing", "evidence": "Groq key not found.", "impact": "None", "recommendation": "Add GROQ_API_KEY to .env"}]

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        where_clause, params = build_where_clause(days, source, category)
        
        # Fetch a sample of 20 recent reviews for the LLM context
        query = f"""
            SELECT category, clean_text 
            FROM nykaa_raw_reviews
            {where_clause}
            ORDER BY review_date DESC
            LIMIT 20
        """
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        
        if not rows:
            return [{"barrier": "No data", "evidence": "No reviews found for these filters.", "impact": "N/A", "recommendation": "Adjust filters."}]
            
        text_data = "\n".join([f"- [{row['category']}] {row['clean_text']}" for row in rows])
        
        prompt = f"""
        You are a product analytics AI. I have given you a set of actual user complaints filtered from our database:
        {text_data}
        
        Generate exactly 2 major barrier insights based ONLY on the evidence provided above.
        Format your response exactly as JSON like this:
        [
          {{
            "barrier": "Short name of barrier",
            "evidence": "Observed evidence from the text",
            "impact": "High/Medium/Low",
            "recommendation": "1 actionable sentence"
          }}
        ]
        Respond with ONLY the raw JSON array.
        """
        
        response = client.chat.completions.create(
            model='qwen/qwen3.8-27b',
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content.strip()
        # Fallback parsing if LLM adds markdown backticks
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        import json
        return json.loads(content)
    except Exception as e:
        print(f"Insight Generation Error: {e}")
        return [{"barrier": "Analysis Error", "evidence": str(e), "impact": "Unknown", "recommendation": "Check backend logs."}]
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
