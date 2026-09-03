# Deployment Plan — Nykaa Fashion Conversion Command Center

> **Backend:** Railway (FastAPI + PostgreSQL + Redis)  
> **Frontend:** Vercel (Vite static site)

---

## Architecture Overview

```
┌─────────────────────┐        API Calls         ┌──────────────────────────────┐
│                     │  ───────────────────────► │                              │
│   Vercel (Frontend) │                           │   Railway (Backend)          │
│   Vite Static Site  │  ◄─────────────────────── │   FastAPI + Uvicorn          │
│                     │        JSON Responses     │                              │
└─────────────────────┘                           │   ┌─────────┐ ┌───────────┐ │
                                                  │   │ Postgres │ │   Redis   │ │
                                                  │   │ pgvector │ │  (cache)  │ │
                                                  │   └─────────┘ └───────────┘ │
                                                  └──────────────────────────────┘
```

---

## Pre-Deployment Code Changes Required

> [!IMPORTANT]
> These code changes **must** be made and committed before deploying.

### 1. Add CORS Middleware to `api.py`

The frontend on Vercel (`*.vercel.app`) will be on a different origin than the Railway backend. Without CORS, all API calls will be blocked by the browser.

**Add this near the top of [`api.py`](file:///c:/Users/Gourav/Desktop/Nykaa%20Fashion/api.py), right after `app = FastAPI(...)`:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nykaa-fashion.vercel.app",   # Your production Vercel URL
        "http://localhost:5173",                # Local Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> [!TIP]
> After your first Vercel deployment, update the `allow_origins` list with the exact Vercel domain you receive.

---

### 2. Make the API Base URL Configurable in the Frontend

Currently, [`main.js`](file:///c:/Users/Gourav/Desktop/Nykaa%20Fashion/frontend/src/main.js#L49) has a hardcoded `http://localhost:8000`. This must point to the Railway backend URL in production.

**Update `main.js` line 49:**

```diff
- const res = await fetch('http://localhost:8000/api/v2/kpis?days=30');
+ const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
+ const res = await fetch(`${API_BASE}/api/v2/kpis?days=30`);
```

This lets Vercel inject the Railway backend URL at build time via the `VITE_API_URL` environment variable.

---

### 3. Add a `Procfile` for Railway

Railway needs to know how to start your app. Create a `Procfile` in the project root:

```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

> [!NOTE]
> Railway dynamically assigns `$PORT`. You must bind to `0.0.0.0` and use `$PORT`.

---

### 4. Add `runtime.txt` (Optional but Recommended)

Specify the Python version to ensure consistency:

```
python-3.10.14
```

---

## Part 1 — Backend Deployment on Railway

### Step 1: Create a Railway Account & Project

1. Go to [railway.app](https://railway.app) and sign up / log in with GitHub.
2. Click **"New Project"** → **"Deploy from GitHub Repo"**.
3. Select the **`Gopo23/Nykaa-Fashion`** repository.

### Step 2: Configure Root Directory

Since the backend is in the **root** of the repo (not in a subfolder), no root directory config is needed. Railway will auto-detect the `requirements.api.txt` or `Procfile`.

> [!IMPORTANT]
> Railway auto-detects `requirements.txt` by default. Since your API dependencies are in `requirements.api.txt`, you must set a custom build command.

**In Railway Project → Settings → Build:**

| Setting | Value |
|---|---|
| **Build Command** | `pip install -r requirements.api.txt` |
| **Start Command** | `uvicorn api:app --host 0.0.0.0 --port $PORT` |

### Step 3: Provision PostgreSQL on Railway

1. In your Railway project, click **"+ New"** → **"Database"** → **"PostgreSQL"**.
2. Railway will create a managed PostgreSQL instance.
3. Go to the PostgreSQL service → **Variables** tab → copy the connection values.
4. Run the [`database_setup.sql`](file:///c:/Users/Gourav/Desktop/Nykaa%20Fashion/database_setup.sql) script against the Railway Postgres instance to create the schema:
   ```bash
   psql $DATABASE_URL -f database_setup.sql
   ```

### Step 4: Provision Redis on Railway

1. In your Railway project, click **"+ New"** → **"Database"** → **"Redis"**.
2. Railway will create a managed Redis instance.
3. Copy the `REDIS_HOST` and `REDIS_PORT` from the Redis service's variables.

### Step 5: Set Environment Variables

In the **backend service** → **Variables** tab, add:

| Variable | Value | Notes |
|---|---|---|
| `DB_HOST` | (from Railway Postgres) | e.g., `postgres.railway.internal` |
| `DB_PORT` | (from Railway Postgres) | Usually `5432` |
| `DB_USER` | (from Railway Postgres) | e.g., `postgres` |
| `DB_PASS` | (from Railway Postgres) | Auto-generated |
| `DB_NAME` | (from Railway Postgres) | e.g., `railway` |
| `GROQ_API_KEY` | Your Groq API key | For AI insights endpoint |
| `REDIS_HOST` | (from Railway Redis) | e.g., `redis.railway.internal` |

> [!CAUTION]
> **Never commit your `.env` file to GitHub.** Your current `.env` contains real credentials. Confirm it is listed in `.gitignore` (it is ✅).

### Step 6: Deploy & Test

1. Railway will automatically deploy on every push to `main`.
2. Go to your service → **Settings** → **"Generate Domain"** to get a public URL.
3. Test the API:
   ```
   https://<your-railway-domain>/api/v2/kpis?days=30
   ```

**Expected Railway Backend URL format:**  
`https://nykaa-fashion-production.up.railway.app`

---

## Part 2 — Frontend Deployment on Vercel

### Step 1: Create a Vercel Account & Import Project

1. Go to [vercel.com](https://vercel.com) and sign up / log in with GitHub.
2. Click **"Add New..."** → **"Project"** → Import `Gopo23/Nykaa-Fashion`.

### Step 2: Configure Build Settings

Since the frontend lives in the `frontend/` subdirectory:

| Setting | Value |
|---|---|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### Step 3: Set Environment Variables

In Vercel → **Project Settings** → **Environment Variables**, add:

| Variable | Value | Notes |
|---|---|---|
| `VITE_API_URL` | `https://<your-railway-domain>` | The Railway backend URL from Part 1, Step 6. **No trailing slash.** |

> [!IMPORTANT]
> Vite only exposes env variables prefixed with `VITE_` to the client-side code. This is why the variable is named `VITE_API_URL`.

### Step 4: Deploy

1. Click **"Deploy"**. Vercel will build and deploy the Vite app.
2. Your frontend will be live at:  
   `https://nykaa-fashion.vercel.app` (or similar)

### Step 5: Update CORS Origins

After getting your Vercel URL, go back to Railway and update the `allow_origins` list in [`api.py`](file:///c:/Users/Gourav/Desktop/Nykaa%20Fashion/api.py) to include the exact Vercel domain. Commit and push.

---

## Post-Deployment Checklist

- [ ] **CORS** — Confirm API calls from Vercel frontend are not blocked
- [ ] **Database** — Verify Railway PostgreSQL has the schema (run `database_setup.sql`)
- [ ] **Data** — Import review data into Railway PostgreSQL (migrate from local CSV/DB)
- [ ] **API Health** — Test `https://<railway-url>/api/v2/kpis?days=30`
- [ ] **Frontend** — Verify all 4 views load correctly on the Vercel URL
- [ ] **AI Insights** — Confirm `GROQ_API_KEY` works on Railway (test `/api/v2/insights`)
- [ ] **Redis Cache** — Verify caching works (check response times)
- [ ] **Environment Variables** — Ensure no secrets are hardcoded or committed
- [ ] **Custom Domain** (optional) — Add your own domain in Vercel/Railway settings

---

## Data Migration

Your local PostgreSQL has the review data. To migrate it to Railway:

```bash
# 1. Export from local
pg_dump -h localhost -p 5434 -U postgres -d postgres -t nykaa_raw_reviews --data-only > data_dump.sql

# 2. Import to Railway (use the DATABASE_URL from Railway)
psql $RAILWAY_DATABASE_URL < data_dump.sql
```

Alternatively, re-run your data ingestion scripts ([`fetch_real_reviews.py`](file:///c:/Users/Gourav/Desktop/Nykaa%20Fashion/fetch_real_reviews.py), [`process_reviews.py`](file:///c:/Users/Gourav/Desktop/Nykaa%20Fashion/process_reviews.py)) with Railway's database credentials.

---

## Cost Estimates

| Service | Free Tier | Notes |
|---|---|---|
| **Railway** | $5 free credit/month (trial) | PostgreSQL + Redis + API server |
| **Vercel** | Generous free tier | Unlimited static deploys for personal projects |

> [!NOTE]
> Railway's free trial gives $5/month. For production use, the Hobby plan starts at $5/month. Vercel's free tier is sufficient for this project.

---

## Summary of Files to Create/Modify

| Action | File | Purpose |
|---|---|---|
| **MODIFY** | [`api.py`](file:///c:/Users/Gourav/Desktop/Nykaa%20Fashion/api.py) | Add CORS middleware |
| **MODIFY** | [`main.js`](file:///c:/Users/Gourav/Desktop/Nykaa%20Fashion/frontend/src/main.js) | Use `VITE_API_URL` env variable |
| **CREATE** | `Procfile` | Railway start command |
| **CREATE** | `runtime.txt` | Pin Python version |
