# Render.com Deployment Guide

## Prerequisites
1. Create a Render.com account
2. Connect your GitHub repository to Render
3. Set up a PostgreSQL database on Render

## Deployment Steps

### 1. Database Setup
1. In your Render dashboard, create a new PostgreSQL database
2. Copy the External Database URL (starts with `postgres://`)
3. Save this URL - you'll need it for the web service

### 2. Web Service Setup
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use these settings:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -e .`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`
   - **Environment**: Python 3.11

### 3. Environment Variables
Set these environment variables in your Render web service:
- `DATABASE_URL`: The PostgreSQL External Database URL from step 1
- `SESSION_SECRET`: Generate a random secret key (32+ characters)
- `FLASK_ENV`: `production`

### 4. Optional: Email Configuration
If you want to enable email functionality, add:
- `GMAIL_USER`: Your Gmail address
- `GMAIL_PASSWORD`: Your Gmail app password

## File Structure
The following files are configured for Render deployment:
- `Procfile`: Heroku-style process file (also works with Render)
- `pyproject.toml`: Python dependencies
- `render.yaml`: Render-specific configuration (optional)

## Deployment Features
- ✅ PostgreSQL database support
- ✅ Automatic SSL/HTTPS
- ✅ Environment variable management
- ✅ Git-based deployments
- ✅ Health checks
- ✅ Logging and monitoring

## Post-Deployment
1. Your app will be available at `https://your-app-name.onrender.com`
2. The database tables will be created automatically on first run
3. Create your first user account through the registration page

## Troubleshooting
- Check the deployment logs in Render dashboard
- Ensure all environment variables are set correctly
- Verify the DATABASE_URL format is correct
- Check that your GitHub repository is public or properly connected