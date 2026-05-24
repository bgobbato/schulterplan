# Deployment Instructions — SchulterPlan to Vercel

## Quick Start (5 minutes)

### Prerequisites
- Vercel account (free at https://vercel.com)
- GitHub account (to connect repository)
- Git installed

### Steps

#### 1. Create a GitHub Repository

```bash
# Initialize git in the project folder
git init
git add .
git commit -m "Initial commit: SchulterPlan deployment-ready"

# Create repo on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/schulterplan.git
git branch -M main
git push -u origin main
```

#### 2. Deploy to Vercel

**Option A: Via Vercel Dashboard (Easiest)**

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Select your GitHub repository (`schulterplan`)
4. Click "Import"
5. Vercel will auto-detect the project settings
6. Click "Deploy"

**Option B: Via Vercel CLI**

```bash
npm install -g vercel
cd schulterplan-vercel
vercel
# Follow prompts, confirm deployment
```

#### 3. Verify Deployment

After deployment, Vercel provides a URL (e.g., `https://schulterplan.vercel.app`)

- **Main planner**: https://schulterplan.vercel.app/
- **Surgery dashboard**: https://schulterplan.vercel.app/surgery-dashboard.html

### Post-Deployment Checklist

- [ ] Main page loads (3D viewer visible)
- [ ] All models load (scapula, implant visible)
- [ ] Measurement tools work (click "📏 Measure")
- [ ] Auto-measure button works (shows inferior/anterior distances)
- [ ] Surgery dashboard responsive on wide screens
- [ ] No 404 errors in browser console

---

## Troubleshooting

### Models not loading
**Problem**: Gray boxes instead of 3D geometry

**Solution**: Check file paths in HTML:
- All paths must be relative (`./data/...` not `/data/...`)
- File extensions must match (case-sensitive on Vercel)

### 404 errors for data files
**Problem**: "Failed to load resource: 404"

**Solution**:
- Ensure all `.stl` and `.obj` files are in `/data/` folder
- Verify `planning.json` exists in `/data/`
- Clear browser cache (Ctrl+F5 / Cmd+Shift+R)

### Performance slow
**Problem**: Rendering lag or stuttering

**Solution**:
- Vercel serves static files with CDN caching — should be fast
- Check browser console for WebGL errors
- Try a different browser (Chrome recommended)

---

## Updates and Maintenance

### Pushing Changes

```bash
# Make code changes locally
git add .
git commit -m "Description of changes"
git push

# Vercel automatically deploys on push to main branch
```

### Reverting to Previous Version

Vercel keeps deployment history:
1. Go to Vercel Dashboard → Project → Deployments
2. Find previous deployment
3. Click "Promote to Production"

---

## Domain Setup (Optional)

To use custom domain (e.g., `schulterplan.example.com`):

1. Go to Vercel Dashboard → Project Settings → Domains
2. Add custom domain
3. Update DNS records as instructed
4. Wait ~30 minutes for DNS propagation

---

## Environment Variables (Optional)

If needed in the future:

1. Vercel Dashboard → Project Settings → Environment Variables
2. Add variables (e.g., `API_URL=...`)
3. Redeploy

---

## Support

For Vercel issues: https://vercel.com/docs  
For code issues: Check browser console (F12)

---

**Deployed**: [Insert URL here after first deployment]  
**Last Updated**: May 24, 2026
