# Vercel Deployment Guide

## Overview

This guide will help you deploy your Review Automation Platform to Vercel, which offers faster cold start times compared to Render.com's free tier.

## Prerequisites

1. **GitHub Repository**: Your code should be pushed to a GitHub repository
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com) (free tier available)
3. **Database**: You'll need a PostgreSQL database (recommendations below)

## Step 1: Database Setup

Since Vercel doesn't include a database, you'll need an external PostgreSQL service:

### Recommended Free PostgreSQL Providers:
- **Neon** (neon.tech) - Free tier with 0.5GB storage
- **Supabase** (supabase.com) - Free tier with 500MB storage
- **ElephantSQL** (elephantsql.com) - Free tier with 20MB storage

### Database Setup Steps:
1. Create account with your chosen provider
2. Create a new PostgreSQL database
3. Copy the connection string (DATABASE_URL)

## Step 2: Vercel Deployment

### Option A: Deploy via Vercel Dashboard
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect it's a Python project

### Option B: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from your project directory
vercel

# Follow the prompts
```

## Step 3: Environment Variables

In your Vercel project dashboard, go to Settings → Environment Variables and add:

### Required Variables:
```
SESSION_SECRET=your-random-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database
```

### Optional Email Variables (for production):
```
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
```

## Step 4: Custom Domain (Optional)

1. In Vercel dashboard, go to Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

## Files Added for Vercel

### `vercel.json`
Configuration file that tells Vercel:
- Entry point: `main.py`
- Runtime: Python
- Route handling: All requests to main.py

### Updated `main.py`
- Exports the Flask app for Vercel
- Maintains compatibility with local development

## Key Differences from Render

| Feature | Render.com | Vercel |
|---------|------------|--------|
| Cold Start | ~30 seconds | ~2-3 seconds |
| Always On | No (free tier) | No (free tier) |
| Database | Included (paid) | External required |
| Deployment | Git push | Git push or CLI |
| Custom Domain | Free | Free |

## Troubleshooting

### Common Issues:

1. **Database Connection Errors**
   - Verify DATABASE_URL is correct
   - Ensure database allows external connections
   - Check firewall settings

2. **Module Import Errors**
   - Ensure all dependencies are in requirements.txt
   - Check Python version compatibility

3. **Static Files Not Loading**
   - Vercel automatically handles static files
   - Ensure files are in `static/` directory

### Environment Variables
Always set these in Vercel dashboard, never in code:
- `SESSION_SECRET`: Random string for Flask sessions
- `DATABASE_URL`: PostgreSQL connection string

## Post-Deployment Checklist

- [ ] Application loads successfully
- [ ] Database connection works
- [ ] User registration/login works
- [ ] Review submission works
- [ ] Email notifications work (if configured)
- [ ] Google redirect works for 4-5 star reviews

## Performance Benefits

With Vercel, you should see:
- **Faster cold starts**: 2-3 seconds vs 30+ seconds
- **Better global performance**: Edge network
- **Automatic HTTPS**: Built-in SSL certificates
- **Git integration**: Auto-deploy on push

## Migration from Render

1. Deploy to Vercel (keep Render running)
2. Test all functionality
3. Update DNS to point to Vercel
4. Delete Render deployment

Your Review Automation Platform will now load much faster on Vercel's infrastructure!