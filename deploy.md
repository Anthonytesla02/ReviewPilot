# Deployment Guide

## Vercel Deployment

This Flask application is configured for Vercel deployment with the following files:

### Configuration Files
- `vercel.json` - Vercel deployment configuration
- `wsgi.py` - WSGI entry point for production
- `Procfile` - Process configuration for deployment
- `runtime.txt` - Python version specification
- `.gitignore` - Files to exclude from version control

### Environment Variables Required

Set these environment variables in your Vercel dashboard:

#### Required Secrets
```
DATABASE_URL=your_postgresql_database_url
SESSION_SECRET=your_secret_key_here
GMAIL_USER=your_gmail_address@gmail.com  
GMAIL_PASSWORD=your_gmail_app_password
```

#### Optional Settings
```
FLASK_ENV=production
```

### Database Setup

The app uses PostgreSQL and is configured to work with:
- Vercel PostgreSQL
- Railway PostgreSQL  
- Any PostgreSQL database accessible via DATABASE_URL

### Gmail Configuration

For production email sending:
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password for your Gmail account
3. Set GMAIL_USER to your full Gmail address
4. Set GMAIL_PASSWORD to the App Password (not your regular password)

### Deployment Steps

1. Connect your GitHub repository to Vercel
2. Set the environment variables in Vercel dashboard
3. Deploy - Vercel will automatically detect it's a Python Flask app
4. Your app will be available at `your-app-name.vercel.app`

### Production Features

✅ Professional HTML email templates with anti-spam headers
✅ Smart review routing (1-3 stars → detailed feedback, 4 stars → admin alert, 5 stars → Google redirect)
✅ Real-time email notifications
✅ Secure session management
✅ Database connection pooling
✅ Error handling and logging
✅ Mobile-responsive design
✅ CSRF protection on all forms