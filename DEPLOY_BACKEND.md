# 🚀 HUNGIE BACKEND DEPLOYMENT GUIDE

## Step 1: Prepare for Railway Deployment

### Files Ready for Deployment:
✅ **prod_server.py** - Production-ready FastAPI server
✅ **requirements-prod.txt** - Python dependencies
✅ **railway.json** - Railway configuration
✅ **Procfile** - Alternative deployment config
✅ **substitutions.py** - Ingredient substitution database
✅ **hungie.db** - Recipe database

## Step 2: Create Railway Account & Deploy

### Option A: Railway CLI (if Git is installed)
1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize and Deploy**:
   ```bash
   railway init
   railway up
   ```

### Option B: Railway Web Interface (Recommended)
1. **Go to Railway**: https://railway.app/
2. **Sign up/Login** with GitHub account
3. **Click "New Project"** 
4. **Choose "Deploy from GitHub repo"**
5. **Connect your GitHub account** if not already connected
6. **Create a new repository** for Hungie or push to existing one

## Step 3: GitHub Repository Setup (if needed)

### If you don't have the code on GitHub yet:
1. **Go to GitHub.com** and create a new repository called "hungie"
2. **Upload these files** via GitHub web interface:
   - `prod_server.py`
   - `requirements-prod.txt` 
   - `railway.json`
   - `Procfile`
   - `substitutions.py`
   - `hungie.db`
   - `.env.example` (rename to remove your actual API key)

### Or use GitHub Desktop:
1. **Download GitHub Desktop**: https://desktop.github.com/
2. **Clone/Create repository**
3. **Add files and commit**
4. **Push to GitHub**

## Step 4: Railway Configuration

### Environment Variables to Set in Railway:
```
OPENAI_API_KEY=your_actual_openai_key_here
ENVIRONMENT=production
```

### In Railway Dashboard:
1. **Go to your project**
2. **Click "Variables" tab**
3. **Add the environment variables above**
4. **Click "Deploy"**

## Step 5: Test Deployment

### Your API will be available at:
```
https://your-project-name.railway.app
```

### Test these endpoints:
- `GET /health` - Health check
- `GET /api/recipes` - Recipe list
- `POST /api/smart-search` - AI chat (with OpenAI key)
- `GET /api/substitutions/browse` - Substitution database

## Step 6: Update Frontend

### In your React app, update the API URL:
```javascript
// frontend/.env.production
REACT_APP_API_URL=https://your-project-name.railway.app
```

## Step 7: Common Issues & Solutions

### Issue: "Module not found"
**Solution**: Check `requirements-prod.txt` has all dependencies

### Issue: "Database not found" 
**Solution**: Ensure `hungie.db` is uploaded to your repository

### Issue: "OpenAI API error"
**Solution**: Verify your OpenAI API key in Railway environment variables

### Issue: "CORS error"
**Solution**: The CORS is configured for production domains. Test with Railway URL first.

## 🎉 SUCCESS!

Once deployed, your Hungie API will be live with:
- ✅ 92+ curated recipes
- ✅ AI-powered chat with substitutions  
- ✅ Smart recipe search
- ✅ Health monitoring
- ✅ Production logging

**Next**: Deploy the React frontend to Vercel and connect it to your Railway API!

---

## Alternative: Quick Test Deployment

### If you want to test quickly without GitHub:

1. **Zip your files**: Create a ZIP with all the files listed above
2. **Use Render.com** or **Heroku** instead
3. **Upload ZIP directly** to these platforms
4. **Set environment variables** in their dashboard
5. **Deploy and test**

The same files will work on any of these platforms!
