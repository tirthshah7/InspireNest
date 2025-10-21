# 🚀 InspireNest Deployment Guide

**Status**: Ready for Deployment  
**Platform**: Railway (Recommended) or Heroku  
**Timeline**: 1-2 hours setup

---

## 🎯 **Deployment Options**

### **Option A: Railway** (RECOMMENDED)
```
Pros:
  ✅ Free tier (500 hours/month)
  ✅ Automatic HTTPS
  ✅ GitHub integration
  ✅ Easy setup (click deploy)
  ✅ Auto-scaling
  ✅ Great for startups

Cost: $0-20/month
Setup Time: 30 minutes
URL: https://inspirenest.up.railway.app
```

### **Option B: Heroku**
```
Pros:
  ✅ Free dyno hours
  ✅ Mature platform
  ✅ Good documentation
  ✅ Add-ons ecosystem

Cons:
  ⚠️  Slower than Railway
  ⚠️  More complex setup

Cost: $0-25/month
Setup Time: 1 hour
```

### **Option C: Digital Ocean / AWS**
```
Pros:
  ✅ Full control
  ✅ Better performance
  ✅ Custom configuration

Cons:
  ⚠️  More complex
  ⚠️  Requires DevOps knowledge

Cost: $12-50/month
Setup Time: 2-4 hours
```

---

## 🚂 **RAILWAY DEPLOYMENT** (Recommended)

### **Step-by-Step**:

**1. Create Railway Account**
```
- Go to https://railway.app
- Sign up with GitHub
- Verify email
```

**2. Create New Project**
```
- Click "New Project"
- Select "Deploy from GitHub repo"
- Connect your repo
- Select the webapp folder
```

**3. Configure Backend Service**
```
- Root Directory: webapp/backend
- Build Command: pip install -r requirements.txt
- Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
- Environment:
  - PYTHONPATH=/app/../../src
```

**4. Configure Frontend Service**
```
- Root Directory: webapp/frontend
- Build Command: npm install && npm run build
- Start Command: npm run preview -- --port $PORT --host 0.0.0.0
- Environment:
  - VITE_API_URL=https://your-backend.railway.app
```

**5. Get URLs**
```
Backend:  https://inspirenest-api-xxx.railway.app
Frontend: https://inspirenest-xxx.railway.app
```

**6. Update Frontend API URL**
```javascript
// In webapp/frontend/src/App.jsx
const API_URL = process.env.VITE_API_URL || 'http://localhost:8000'
```

**7. Custom Domain** (Optional)
```
- Buy domain (inspirenest.com)
- Add CNAME record in Railway
- Wait for DNS propagation
- Access at: https://app.inspirenest.com
```

---

## 🐳 **DOCKER DEPLOYMENT**

### **Using Docker Compose** (Local/VPS):

**1. Build and Run**:
```bash
cd webapp
docker-compose up --build
```

**2. Access**:
```
Backend:  http://localhost:8000
Frontend: http://localhost:3000
```

**3. Deploy to VPS** (DigitalOcean, AWS, etc.):
```bash
# On your VPS
git clone <your-repo>
cd webapp
docker-compose up -d

# Access via server IP
http://your-server-ip:3000
```

**4. Production Setup**:
```bash
# Add nginx reverse proxy
# Add SSL certificate (Let's Encrypt)
# Configure domain
```

---

## 🔒 **PRODUCTION CHECKLIST**

### **Before Deploying**:
```
✅ Update CORS origins (no wildcard '*')
✅ Add environment variables
✅ Set up error tracking (Sentry)
✅ Add analytics (PostHog, Mixpanel)
✅ Configure rate limiting
✅ Set up file size limits
✅ Add backup strategy
✅ Configure monitoring
✅ Set up logging
✅ Security audit
```

### **After Deploying**:
```
✅ Test all endpoints
✅ Test file upload
✅ Test nesting
✅ Test download
✅ Check error handling
✅ Monitor performance
✅ Set up alerts
```

---

## 📊 **MONITORING & ANALYTICS**

### **Essential Metrics**:
```
Traffic:
  - Daily active users
  - Nesting jobs per day
  - Success/failure rate

Performance:
  - API response time
  - Nesting processing time
  - Download speed

Business:
  - Conversion rate (free → paid)
  - Churn rate
  - MRR (Monthly Recurring Revenue)
```

### **Tools to Add**:
```
Error Tracking: Sentry (free tier)
Analytics: PostHog or Mixpanel (free tier)
Monitoring: Railway built-in or UptimeRobot
Logging: Railway logs or Papertrail
```

---

## 💰 **PRICING & MONETIZATION**

### **Implement Usage Limits**:
```python
# Add to backend/main.py

from datetime import datetime
from collections import defaultdict

# Simple in-memory usage tracking (use database in production)
usage_tracker = defaultdict(int)

@app.post("/api/nest/{job_id}")
async def nest_parts(...):
    # Check usage limit
    user_id = "anonymous"  # Get from auth in future
    usage_tracker[user_id] += 1
    
    # Free tier limit: 10 nests/month
    if usage_tracker[user_id] > 10:
        raise HTTPException(
            status_code=403, 
            detail="Free tier limit reached. Please upgrade to Pro."
        )
    
    # ... rest of nesting code
```

### **Add Stripe Integration** (Future):
```bash
pip install stripe

# Create subscription checkout
# Handle webhooks
# Manage subscriptions
```

---

## 🌍 **SCALING STRATEGY**

### **Small Scale** (1-100 users):
```
Platform: Railway free tier
Cost: $0-20/month
Handles: ~1,000 nesting jobs/month
```

### **Medium Scale** (100-1,000 users):
```
Platform: Railway Pro or Heroku
Cost: $50-200/month
Handles: ~10,000 nesting jobs/month
Features: Auto-scaling, better performance
```

### **Large Scale** (1,000-10,000 users):
```
Platform: AWS/DigitalOcean with Kubernetes
Cost: $200-1,000/month
Handles: ~100,000+ nesting jobs/month
Features: Multi-region, CDN, queue workers
```

---

## 🎯 **QUICK DEPLOY COMMANDS**

### **Railway (Easiest)**:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd webapp
railway init

# Deploy backend
cd backend
railway up

# Deploy frontend
cd ../frontend
railway up

# Done! Get URLs from Railway dashboard
```

### **Heroku**:
```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create apps
heroku create inspirenest-api
heroku create inspirenest-app

# Deploy backend
cd webapp/backend
git subtree push --prefix webapp/backend heroku main

# Deploy frontend
cd ../frontend
git subtree push --prefix webapp/frontend heroku main
```

---

## ✅ **DEPLOYMENT READY**

**Status**: All deployment files created ✅

**What's Ready**:
- ✅ Backend Dockerfile
- ✅ Frontend Dockerfile
- ✅ docker-compose.yml
- ✅ Deployment guide
- ✅ Production checklist

**Next Action**: Deploy to Railway (30 minutes) or test locally with Docker

---

**Generated**: 2025-10-20  
**Status**: ✅ **Ready for Deployment**  
**Recommendation**: Deploy to Railway for easiest setup

