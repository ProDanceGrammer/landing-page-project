# Deployment Guide

Complete step-by-step guide to deploy the Lead Processing Landing Page to production.

## Architecture Overview

- **Frontend**: Vercel (https://vasyl-yarmolenko.online)
- **Backend**: Render (https://landing-backend.onrender.com)
- **Database**: Neon PostgreSQL (serverless)
- **AI**: Ollama (primary) + OpenAI (fallback)
- **Monitoring**: UptimeRobot, Betterstack, Cronitor, GitHub Actions

## Prerequisites

Before starting, you'll need accounts on:

1. **Vercel** - https://vercel.com (free tier)
2. **Render** - https://render.com (free tier)
3. **Neon** - https://neon.tech (free tier)
4. **GitHub** - https://github.com (repository access)
5. **UptimeRobot** - https://uptimerobot.com (optional, for monitoring)
6. **Betterstack** - https://betterstack.com (optional, for monitoring)
7. **Cronitor** - https://cronitor.io (optional, for monitoring)

## Part 1: Database Setup (Neon PostgreSQL)

### Step 1: Create Neon Account

1. Go to https://neon.tech
2. Sign up with GitHub (recommended)
3. Click "Create Project"
4. Project name: `landing-backend`
5. Region: Choose closest to your users
6. PostgreSQL version: 16 (latest)

### Step 2: Get Database URL

1. After project creation, click "Connection Details"
2. Copy the connection string (starts with `postgresql://`)
3. Save it temporarily - you'll need it for Render

**Format:**
```
postgresql://username:password@host/database?sslmode=require
```

### Step 3: Initialize Database

The database schema will be created automatically on first run, but you can verify:

```sql
-- This is handled by the application, but FYI the schema is:
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    received_at TIMESTAMP DEFAULT NOW(),
    raw_json TEXT NOT NULL,
    name TEXT,
    email TEXT NOT NULL,
    phone TEXT,
    company TEXT,
    message TEXT,
    ai_summary TEXT,
    temperature TEXT,
    priority_score INTEGER,
    classification_reasoning TEXT,
    status TEXT DEFAULT 'processed'
);
```

---

## Part 2: Backend Deployment (Render)

### Step 1: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 2: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `landing-page-project`
3. Configure the service:
   - **Name**: `landing-backend`
   - **Region**: Oregon (US West) or closest
   - **Branch**: `main` (or `master`)
   - **Root Directory**: (leave blank)
   - **Environment**: Python 3
   - **Build Command**: `bash render-build.sh`
   - **Start Command**: `ollama serve & sleep 5 && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### Step 3: Set Environment Variables

In Render dashboard, go to "Environment" and add:

```
AI_BACKEND=ollama
OLLAMA_MODEL=phi3
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=<your-openai-key>
OPENAI_MODEL=gpt-3.5-turbo
TELEGRAM_BOT_TOKEN=<your-telegram-token>
TELEGRAM_CHAT_ID=<your-telegram-chat-id>
DATABASE_URL=<your-neon-postgres-url>
DATABASE_TYPE=postgres
```

**Important:**
- Get TELEGRAM_BOT_TOKEN from your `.env` file
- Get TELEGRAM_CHAT_ID from your `.env` file
- Get DATABASE_URL from Neon (Part 1)
- Get OPENAI_API_KEY from https://platform.openai.com/api-keys

### Step 4: Get Deploy Hook

1. In Render service settings, go to "Settings"
2. Scroll to "Deploy Hook"
3. Copy the webhook URL (you'll need this for GitHub Actions)
4. Format: `https://api.render.com/deploy/srv-xxxxx?key=yyyyy`

### Step 5: Deploy

1. Click "Manual Deploy" → "Deploy latest commit"
2. Wait 5-10 minutes for:
   - Ollama installation
   - Phi-3 model download (1.6GB)
   - Python dependencies
   - Service startup

**Note:** First deployment takes ~10 minutes. Subsequent deploys are faster.

---

## Part 3: Frontend Deployment (Vercel)

### Step 1: Create Vercel Account

1. Go to https://vercel.com
2. Sign up with GitHub
3. Authorize Vercel to access your repositories

### Step 2: Import Project

1. Click "Add New..." → "Project"
2. Import `landing-page-project` repository
3. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: (leave blank)
   - **Build Command**: (leave blank - static site)
   - **Output Directory**: `static`
   - **Install Command**: (leave blank)

### Step 3: Configure Domain

1. After deployment, go to "Settings" → "Domains"
2. Add custom domain: `vasyl-yarmolenko.online`
3. Add www redirect: `www.vasyl-yarmolenko.online`
4. Vercel will show DNS records to add

### Step 4: Update DNS

Go to your domain registrar (where you bought vasyl-yarmolenko.online) and add these records:

**Vercel will provide exact values, but typically:**
```
Type    Name    Value                   TTL
A       @       76.76.21.21            Auto
CNAME   www     cname.vercel-dns.com   Auto
```

**DNS Propagation:** Takes 5-60 minutes. Check at https://dnschecker.org

### Step 5: Get Vercel Tokens

For GitHub Actions, you need:

1. **VERCEL_TOKEN**:
   - Go to https://vercel.com/account/tokens
   - Create new token: "GitHub Actions"
   - Copy and save

2. **VERCEL_ORG_ID**:
   - Go to Settings → General
   - Copy "Organization ID"

3. **VERCEL_PROJECT_ID**:
   - Go to Project Settings → General
   - Copy "Project ID"

---

## Part 4: GitHub Actions CI/CD

### Step 1: Add GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add repository secrets:

```
VERCEL_TOKEN=<from-vercel-account-tokens>
VERCEL_ORG_ID=<from-vercel-settings>
VERCEL_PROJECT_ID=<from-vercel-project-settings>
RENDER_DEPLOY_HOOK=<from-render-deploy-hook>
```

### Step 2: Verify Workflows

GitHub Actions workflows are already in `.github/workflows/`:
- `deploy.yml` - Runs tests, deploys to Vercel + Render
- `keep-warm.yml` - Pings backend every 10 minutes

### Step 3: Test CI/CD

1. Make a small change (e.g., edit README.md)
2. Commit and push to `main` branch
3. Go to GitHub → Actions tab
4. Watch the workflow run
5. Verify deployments:
   - Vercel: https://vasyl-yarmolenko.online
   - Render: https://landing-backend.onrender.com/health

---

## Part 5: Monitoring Setup (Optional but Recommended)

### UptimeRobot

1. Go to https://uptimerobot.com
2. Sign up (free tier: 50 monitors)
3. Add New Monitor:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: Landing Backend
   - **URL**: https://landing-backend.onrender.com/ping
   - **Monitoring Interval**: 5 minutes
4. Add alert contacts (email)

### Betterstack

1. Go to https://betterstack.com
2. Sign up (free tier)
3. Create Uptime Monitor:
   - **URL**: https://landing-backend.onrender.com/ping
   - **Check Interval**: 3 minutes
   - **Regions**: Multiple (global)
4. Add incident notifications

### Cronitor

1. Go to https://cronitor.io
2. Sign up (free tier: 5 monitors)
3. Create Heartbeat:
   - **Name**: Landing Backend Warmup
   - **Schedule**: Every 10 minutes
   - **Ping URL**: https://landing-backend.onrender.com/ping

**Combined Effect:**
- GitHub Actions: Every 10 min
- UptimeRobot: Every 5 min
- Betterstack: Every 3 min
- Cronitor: Every 10 min

= Backend stays warm 24/7, zero cold starts! ✅

---

## Part 6: Migrate Existing Data (Optional)

If you have existing leads in SQLite:

### Step 1: Add DATABASE_URL to .env

```bash
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
```

### Step 2: Run Migration Script

```bash
python migrate_sqlite_to_pg.py
```

Output:
```
==================================================
SQLite to PostgreSQL Migration Script
==================================================
Connecting to SQLite database...
Connecting to PostgreSQL database...
Creating PostgreSQL table...
Fetching leads from SQLite...
Migrating 15 leads...
✅ Successfully migrated 15 leads!
```

---

## Part 7: Testing & Verification

### Automated Test Script

```bash
bash test_deployment.sh
```

Output:
```
==================================================
Testing Deployment
==================================================

✓ Testing frontend at https://vasyl-yarmolenko.online...
  ✅ Frontend is live!

✓ Testing backend ping...
  ✅ Backend ping successful!

✓ Testing backend health...
  ✅ Backend health check passed!

✓ Testing lead submission...
  ✅ Lead submission successful!

==================================================
✅ All tests passed!
==================================================
```

### Manual Testing Checklist

- [ ] Frontend loads: https://vasyl-yarmolenko.online
- [ ] Landing page displays correctly
- [ ] Form validation works (try submitting empty)
- [ ] Submit a test lead via form
- [ ] Check Telegram for notification
- [ ] Verify lead in Neon database
- [ ] Check Render logs for processing
- [ ] Test cold start (wait 20 min, submit again)
- [ ] Verify monitoring services show "Up"
- [ ] GitHub Actions shows green checkmarks

---

## Troubleshooting

### Frontend Issues

**Site not loading:**
- Check Vercel deployment status
- Verify DNS propagation: https://dnschecker.org
- Check browser console for errors

**Form not submitting:**
- Check Network tab in DevTools
- Verify BACKEND_URL in static/index.html
- Check CORS errors in console

### Backend Issues

**Render deployment failed:**
- Check Render logs for errors
- Verify render-build.sh has execute permissions
- Ollama installation may timeout (retry deploy)

**Cold starts still happening:**
- Verify GitHub Actions cron is running
- Check UptimeRobot is active
- Ensure monitoring services are pinging /ping not /health

**AI not working:**
- Check Ollama logs in Render
- Verify OPENAI_API_KEY is set correctly
- Test OpenAI fallback by setting AI_BACKEND=openai

**Database errors:**
- Verify DATABASE_URL is correct
- Check Neon dashboard for connection limits
- Ensure DATABASE_TYPE=postgres is set

### Common Errors

**Error: "DATABASE_URL is required"**
```
Solution: Add DATABASE_URL to Render environment variables
```

**Error: "Ollama model not found"**
```
Solution: Wait for build to complete (downloads 1.6GB model)
Or switch to smaller model: OLLAMA_MODEL=gemma:2b
```

**Error: "GitHub Actions workflow failed"**
```
Solution: Check GitHub Secrets are set correctly
Verify VERCEL_TOKEN, RENDER_DEPLOY_HOOK are valid
```

---

## Cost Summary

| Service | Plan | Cost | Usage |
|---------|------|------|-------|
| Vercel | Hobby | **$0** | 100 GB bandwidth |
| Render | Free | **$0** | Spins down after 15 min |
| Neon | Free | **$0** | 0.5 GB storage |
| UptimeRobot | Free | **$0** | 50 monitors |
| Betterstack | Free | **$0** | 1 monitor |
| Cronitor | Free | **$0** | 5 monitors |
| GitHub Actions | Free | **$0** | 2000 min/month |
| OpenAI | Pay-as-go | **~$0.50/100 leads** | Fallback only |
| **Total** | | **$0/month** | |

---

## Maintenance

### Regular Tasks

**None!** Everything is automated:
- GitHub Actions deploys on push
- Monitoring keeps backend warm
- SSL certificates auto-renew
- Database backups (Neon handles this)

### Monitoring Dashboards

- **Vercel**: https://vercel.com/dashboard
- **Render**: https://dashboard.render.com
- **Neon**: https://console.neon.tech
- **GitHub Actions**: https://github.com/ProDanceGrammer/landing-page-project/actions
- **UptimeRobot**: https://uptimerobot.com/dashboard

### Logs

- **Frontend**: Vercel dashboard → Project → Logs
- **Backend**: Render dashboard → Service → Logs
- **Database**: Neon dashboard → Monitoring
- **CI/CD**: GitHub Actions → Workflow runs

---

## Next Steps

After successful deployment:

1. **Analytics**: Add Vercel Analytics or Google Analytics
2. **Error Tracking**: Add Sentry for backend errors
3. **Email Notifications**: Add SendGrid alongside Telegram
4. **Admin Dashboard**: Build UI to view/manage leads
5. **A/B Testing**: Test different landing page variants
6. **SEO**: Add meta tags, sitemap, robots.txt
7. **Performance**: Monitor with Lighthouse

---

## Support

If you encounter issues:

1. Check this DEPLOYMENT.md guide
2. Review troubleshooting section
3. Check service status pages:
   - Vercel: https://vercel-status.com
   - Render: https://status.render.com
   - Neon: https://neonstatus.com
4. Review GitHub Actions logs
5. Check Render service logs

---

**Last Updated**: 2026-06-10  
**Deployment Status**: Ready for Production ✅
