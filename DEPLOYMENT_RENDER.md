# 🚀 Deployment Guide: Render.com

## Prerequisites
- GitHub account with this repo pushed
- Render.com account (free)
- OpenWeather API key (optional but recommended)

---

## Step 1: Push Code to GitHub

```bash
git init
git add .
git commit -m "Deploy AQI system to Render"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/aqi-system.git
git push -u origin main
```

---

## Step 2: Create Render Account & Link GitHub

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

---

## Step 3: Deploy via render.yaml

### Option A: Deploy using Dashboard (Easiest)

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Select your GitHub repo containing `render.yaml`
4. Render auto-detects the config → Click **"Deploy"**
5. Wait 3-5 minutes for services to start

### Option B: Deploy Individual Services

If Blueprint fails, deploy manually:

1. **Create PostgreSQL Database:**
   - Click **"New +"** → **"PostgreSQL"**
   - Name: `aqi-db`
   - Plan: **Free** (500MB storage)
   - Create database
   - Copy internal connection string

2. **Deploy FastAPI Backend:**
   - Click **"New +"** → **"Web Service"**
   - Select your repo
   - Settings:
     - **Name:** `aqi-api`
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt && python backend/db/init_db.py`
     - **Start Command:** `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
     - **Plan:** Free
   - Add Environment Variables:
     ```
     DATABASE_URL=postgresql://user:password@host:port/dbname
     TRAINING_DATA_PATH=data/raw/aqi.csv
     OPENWEATHER_API_KEY=your_key_here (optional)
     ```
   - Deploy

3. **Deploy Streamlit Dashboard:**
   - Click **"New +"** → **"Web Service"**
   - Select your repo
   - Settings:
     - **Name:** `aqi-dashboard`
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
     - **Plan:** Free
   - Add Environment Variables:
     ```
     DATABASE_URL=postgresql://user:password@host:port/dbname
     TRAINING_DATA_PATH=data/raw/aqi.csv
     OPENWEATHER_API_KEY=your_key_here (optional)
     ```
   - Deploy

---

## Step 4: Verify Deployment

Once all services are running (green status):

```
✅ aqi-api: https://aqi-api.onrender.com
✅ aqi-dashboard: https://aqi-dashboard.onrender.com
✅ aqi-db: PostgreSQL active
```

**Test Backend:**
```bash
curl https://aqi-api.onrender.com/health
# Expected: {"status":"ok"}
```

**Access Dashboard:**
Open: `https://aqi-dashboard.onrender.com`

---

## Step 5: Update Configuration

### Update app.py to use remote API:

Replace `localhost:8000` with your deployed API URL:

```python
# frontend/services/prediction_service.py
API_BASE_URL = "https://aqi-api.onrender.com"  # Change this
```

### Update .env.example:

```
DATABASE_URL=postgresql://username:password@hostname/dbname
TRAINING_DATA_PATH=data/raw/aqi.csv
OPENWEATHER_API_KEY=your_key_here
```

---

## Step 6: Continuous Deployment

Every time you push to GitHub:
```bash
git push origin main
```

Render auto-redeploys! ✅

---

## Troubleshooting

### Dashboard Not Loading?
- Check logs: **Dashboard** → **Service** → **Logs**
- Common: `DATABASE_URL` not set or incorrect

### API Returns 500 Error?
- Verify `DATABASE_URL` includes `postgresql://` scheme
- Check if database tables were initialized

### Database Connection Timeout?
- Ensure `render.yaml` has `preDeployCommand: python backend/db/init_db.py`
- Restart service: Dashboard → Service → **Restart**

### Free Tier Limitations?
- Free databases spin down after 15 mins of inactivity (slow startup)
- Free web services auto-suspend after 15 mins (Streamlit will reload on access)
- Upgrade to paid if you need always-on service

---

## Cost Breakdown (All Free! 🎉)

| Service | Tier | Cost |
|---------|------|------|
| FastAPI Backend | Free | $0 |
| Streamlit Dashboard | Free | $0 |
| PostgreSQL Database | Free | $0 |
| **Total Monthly** | — | **$0** |

---

## Alternative: Switch Database Later

To upgrade from PostgreSQL free to production:

1. Create managed PostgreSQL (paid tier)
2. Update `DATABASE_URL` env var
3. Render auto-migrates data

---

## Next Steps

1. ✅ Push repo to GitHub
2. ✅ Create Render account
3. ✅ Deploy via render.yaml or manual setup
4. ✅ Update remote API URLs
5. ✅ Access dashboard at https://aqi-dashboard.onrender.com

**Questions?** Check [Render Docs](https://render.com/docs)
