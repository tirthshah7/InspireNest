# 🚀 Free Deployment Guide for InspireNest

Deploy your InspireNest application for FREE with these options!

---

## 🌟 Option 1: Render.com (RECOMMENDED - Easiest)

**Best for:** Full-stack apps with minimal setup

### Features:
- ✅ Free subdomain: `inspirenest-backend.onrender.com`
- ✅ Automatic deploys from GitHub
- ✅ Free tier: 750 hours/month
- ✅ Supports Python + Node.js
- ⚠️ Sleeps after 15 min of inactivity (wakes up in ~30s)

### Setup Steps:

1. **Sign up at Render**
   - Go to: https://render.com
   - Sign up with your GitHub account (tirthshah7)

2. **Deploy Backend (FastAPI)**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `tirthshah7/InspireNest`
   - Configure:
     ```
     Name:           inspirenest-backend
     Region:         Oregon (US West)
     Branch:         main
     Root Directory: webapp/backend
     Runtime:        Python 3
     Build Command:  pip install -r requirements.txt
     Start Command:  uvicorn main:app --host 0.0.0.0 --port $PORT
     Plan:           Free
     ```
   - Add Environment Variables:
     ```
     PYTHON_VERSION=3.9.0
     ```
   - Click "Create Web Service"

3. **Deploy Frontend (React)**
   - Click "New +" → "Static Site"
   - Connect your GitHub repository: `tirthshah7/InspireNest`
   - Configure:
     ```
     Name:           inspirenest-frontend
     Branch:         main
     Root Directory: webapp/frontend
     Build Command:  npm install && npm run build
     Publish Dir:    dist
     ```
   - Add Environment Variable:
     ```
     VITE_API_URL=https://inspirenest-backend.onrender.com
     ```
   - Click "Create Static Site"

4. **Access Your App**
   - Backend API: `https://inspirenest-backend.onrender.com`
   - Frontend: `https://inspirenest-frontend.onrender.com`
   - API Docs: `https://inspirenest-backend.onrender.com/docs`

---

## 🔥 Option 2: Railway.app (Developer Friendly)

**Best for:** Easy deployment with generous free tier

### Features:
- ✅ Free subdomain: `inspirenest.up.railway.app`
- ✅ $5 free credits monthly
- ✅ Great Docker support
- ✅ Automatic HTTPS

### Setup Steps:

1. **Sign up at Railway**
   - Go to: https://railway.app
   - Sign in with GitHub

2. **Deploy from GitHub**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `tirthshah7/InspireNest`
   - Railway auto-detects and deploys both services

3. **Configure Services**
   - Backend will be at: `https://inspirenest-backend.railway.app`
   - Frontend will be at: `https://inspirenest.railway.app`

4. **Set Environment Variables**
   - In backend service settings, add:
     ```
     PORT=8000
     ```
   - In frontend service settings, add:
     ```
     VITE_API_URL=https://inspirenest-backend.railway.app
     ```

---

## ☁️ Option 3: Vercel (Frontend) + Render (Backend)

**Best for:** Blazing fast frontend with separate backend

### Frontend on Vercel:

1. **Sign up at Vercel**
   - Go to: https://vercel.com
   - Sign in with GitHub

2. **Import Project**
   - Click "Add New" → "Project"
   - Import `tirthshah7/InspireNest`
   - Configure:
     ```
     Framework Preset:  Vite
     Root Directory:    webapp/frontend
     Build Command:     npm run build
     Output Directory:  dist
     ```

3. **Add Environment Variable**
   ```
   VITE_API_URL=https://inspirenest-backend.onrender.com
   ```

4. **Deploy**
   - Your frontend will be at: `https://inspirenest.vercel.app`

### Backend on Render:
- Follow Render backend steps from Option 1

---

## 🐳 Option 4: Fly.io (Docker-based)

**Best for:** Docker enthusiasts

### Features:
- ✅ Free subdomain: `inspirenest.fly.dev`
- ✅ 3 shared VMs free
- ✅ Docker-native
- ✅ Global deployment

### Setup Steps:

1. **Install Fly CLI**
   ```bash
   brew install flyctl  # macOS
   # or
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up and login**
   ```bash
   fly auth signup
   fly auth login
   ```

3. **Deploy Backend**
   ```bash
   cd webapp/backend
   fly launch --name inspirenest-backend
   # Follow prompts, select free tier
   fly deploy
   ```

4. **Deploy Frontend**
   ```bash
   cd webapp/frontend
   fly launch --name inspirenest-frontend
   # Follow prompts
   fly deploy
   ```

---

## 🆓 Option 5: Heroku (Classic Choice)

**Note:** Heroku removed free tier, but you get $5 credits with GitHub Student Pack

### Setup:
1. Sign up: https://heroku.com
2. Install Heroku CLI: `brew install heroku/brew/heroku`
3. Deploy:
   ```bash
   heroku create inspirenest-backend
   git push heroku main
   ```

---

## 📊 Comparison Table

| Platform | Frontend | Backend | Custom Domain | Sleep Policy | Best For |
|----------|----------|---------|---------------|--------------|----------|
| **Render** | ✅ Static | ✅ Free | ✅ Free | 15 min | Full-stack |
| **Railway** | ✅ Free | ✅ Free | ✅ Free | No sleep | Docker apps |
| **Vercel** | ✅ Best | ❌ Paid | ✅ Free | No sleep | Frontend |
| **Fly.io** | ✅ Free | ✅ Free | ✅ Free | No sleep | Docker |
| **Netlify** | ✅ Great | ❌ No | ✅ Free | No sleep | Static sites |

---

## 🎯 My Recommendation for InspireNest

**Use Render (Option 1)** because:
1. ✅ Easiest setup (no CLI needed)
2. ✅ Perfect for Python + React
3. ✅ Automatic deployments from GitHub
4. ✅ Free SSL certificates
5. ✅ Good for portfolio projects
6. ✅ Your URL: `https://inspirenest-backend.onrender.com`

---

## 🔧 Update Your Frontend API URL

Before deploying, update your frontend to use the deployed backend URL:

**File:** `webapp/frontend/src/App.jsx`

```javascript
// Change this line (around line 20-25):
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// To use environment variable from deployment:
const API_URL = import.meta.env.VITE_API_URL || 'https://inspirenest-backend.onrender.com';
```

---

## 📝 After Deployment

1. **Test Your Deployment**
   - Visit your frontend URL
   - Try uploading a DXF file
   - Test the nesting algorithms
   - Check API documentation at `/docs`

2. **Update GitHub README**
   - Add "Live Demo" section with links
   - Add deployment badges

3. **Share Your Live App**
   - Add to LinkedIn profile
   - Share on Twitter
   - Add to resume
   - Show to recruiters!

---

## 🐛 Troubleshooting

### Backend won't start?
- Check logs in Render dashboard
- Verify all dependencies in requirements.txt
- Check PORT environment variable

### Frontend can't connect to backend?
- Verify VITE_API_URL is correct
- Check CORS settings in backend
- Test backend API directly at `/docs`

### App sleeps (Render free tier)?
- Use a service like https://uptimerobot.com to ping your app every 5 minutes
- Or upgrade to paid tier for always-on

---

## 💰 Cost Breakdown

**For FREE deployment:**
- Render: $0/month (750 hours free)
- Railway: $0/month ($5 credits)
- Vercel: $0/month (frontend)
- Total: **$0/month** 🎉

**To avoid sleeping (optional):**
- Render Standard: $7/month (always-on)
- Railway Pro: $5 credits monthly
- Fly.io: Free for 3 VMs

---

## 🚀 Ready to Deploy?

**Quickest Path:**
1. Go to https://render.com
2. Sign up with GitHub
3. Connect InspireNest repository
4. Deploy backend + frontend
5. Share your live app! 🎉

Your InspireNest will be live at:
- Frontend: `https://inspirenest.onrender.com`
- Backend: `https://inspirenest-backend.onrender.com`
- API Docs: `https://inspirenest-backend.onrender.com/docs`

---

**Need help? Just ask!** 😊

