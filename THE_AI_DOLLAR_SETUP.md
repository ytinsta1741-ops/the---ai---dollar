# 🚀 THE AI DOLLAR - Complete Automation Setup Guide

**Channel:** The AI Dollar  
**Instagram:** @theaidollar1741  
**Posting Times:** 4 PM, 8 PM, 1 AM KSA (Saudi Arabia UTC+3)  
**Hosting:** Render.com (Cloud)  
**Cost:** $0 (100% Free)

---

## ⚡ QUICK START (5 Steps)

### Step 1: Setup YouTube API
1. Go to: https://console.cloud.google.com/
2. Create new project "The AI Dollar"
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials.json

### Step 2: Setup Instagram
1. Create Instagram Business Account (if not already)
2. Go to: https://www.instagram.com/settings/apps-and-websites/
3. Keep username/password safe (for browser automation)

### Step 3: Create n8n Workflow
1. Use workflow JSON provided below
2. Import into n8n
3. Add YouTube & Instagram credentials

### Step 4: Deploy to Render.com
1. Use Render deployment guide below
2. Set environment variables
3. Start workflow

### Step 5: Launch!
1. First video generates automatically
2. Posts to YouTube at 4 PM KSA
3. Posts to Instagram at 4 PM KSA
4. Repeats at 8 PM and 1 AM

---

## 📺 YOUTUBE API SETUP

### Get API Key:

```
1. Go to https://console.cloud.google.com/
2. Click "Create Project"
3. Name: "The AI Dollar"
4. Enable APIs:
   - YouTube Data API v3
   - Google Drive API (optional)
5. Create OAuth 2.0 credentials
6. Application type: Desktop
7. Download JSON file
8. Save as: youtube_credentials.json
```

### Authenticate (First Time):

```bash
# This will open browser, you authorize once
python3 -c "
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'youtube_credentials.json',
    scopes=['https://www.googleapis.com/auth/youtube.upload']
)
creds = flow.run_local_server()
print('✅ Authorized!')
"
```

---

## 📸 INSTAGRAM AUTOMATION SETUP

### Browser Automation (for posting):

```python
# Instagram uses browser automation (no public API for posting)
# n8n will:
# 1. Use Puppeteer to open browser
# 2. Log in with credentials
# 3. Post video automatically
# 4. Close browser

# Credentials needed:
INSTAGRAM_USERNAME = "theaidollar1741"
INSTAGRAM_PASSWORD = "your_password"  # Store in .env
```

---

## 🔄 n8n WORKFLOW SETUP

### What it does:

```
Every day at 4 PM, 8 PM, 1 AM KSA:

1. Generate daily script ↓
2. Create voiceover ↓
3. Download B-roll ↓
4. Edit video (FFmpeg) ↓
5. Upload to YouTube ↓
6. Post to Instagram ↓
7. Log result ↓
```

### Install n8n Locally (for testing):

```bash
npm install -g n8n
n8n start
# Open: http://localhost:5678
```

### Or Use n8n Cloud (Free tier):

```
1. Go to https://n8n.io/
2. Sign up free
3. Create new workflow
4. Import JSON below
```

---

## 🎯 NEXT STEPS

1. Read this entire guide (15 mins)
2. Get YouTube API key (10 mins)
3. Run: pip install -r requirements.txt (5 mins)
4. Edit .env with your credentials (5 mins)
5. Test: python3 video_generator.py (5 mins)
6. Deploy to Render.com (30 mins)

**Total: ~60 minutes**

---

## 🎬 READY TO LAUNCH?

Once deployed:

✅ Automation runs 24/7
✅ Posts 3 videos daily (optimal times)
✅ No manual work needed
✅ Scales to multiple channels

**Expected Results (First 30 Days):**
- 0-5K initial subscribers
- 5K-50K total views
- 0-5 early monetization

**Expected Results (90 Days):**
- 50K-500K subscribers
- 500K-5M views
- $500-5K monthly

---

**Go make money with AI! 🚀**
