# Review Automation Platform

## Overview

This is a Flask-based web application that automates customer review management for businesses. The platform allows business owners to manage customers, send automated review requests via email, and handle incoming reviews with intelligent routing based on ratings.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (July 28, 2025)

✅ **Smart Review Routing System**: Implemented intelligent rating-based routing:
   - 1-3 stars → Detailed feedback form with issue categories
   - 4 stars → Admin notification for improvement opportunities
   - 5 stars → Auto-redirect to Google Reviews with countdown timer

✅ **Production Email System**: Gmail SMTP integration with anti-spam headers and professional HTML templates

✅ **Vercel Deployment Ready**: Created all necessary deployment files (vercel.json, wsgi.py, Procfile, runtime.txt, deploy.md)

✅ **Database Optimization**: Fixed Google Business URL field length issue, updated to TEXT type

✅ **Enhanced User Experience**: Visual star ratings, auto-redirect functionality, detailed feedback collection

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (default) or PostgreSQL support
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for form handling and validation
- **Email Service**: SMTP integration (currently configured for Gmail)

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JavaScript with Bootstrap components

### Database Design
- **User Model**: Stores business owner accounts with authentication
- **Customer Model**: Manages customer information and appointment details
- **ReviewTemplate Model**: Email templates for review requests
- **Review Model**: Customer reviews and ratings
- **ReviewRequest Model**: Tracks sent review requests and their status

## Key Components

### Authentication System
- User registration and login with password hashing (Werkzeug)
- Session-based authentication using Flask-Login
- Protected routes requiring authentication

### Customer Management
- Add, edit, and manage customer information
- Track appointment dates and service types
- Customer database with search and pagination

### Email Template System
- Customizable email templates for review requests
- Variable substitution (customer_name, business_name, review_link)
- Default template system

### Review Processing
- Public review submission forms (accessible via unique tokens)
- Intelligent routing: 5-star reviews → Google Business Profile, <5 stars → internal handling
- Admin response system for negative reviews

### Dashboard & Analytics
- Business metrics and review statistics
- Recent activity tracking
- Customer and review overview

## Data Flow

1. **Customer Onboarding**: Business owners add customers to the system
2. **Review Request**: Automated emails sent with unique review links
3. **Review Submission**: Customers submit reviews via public forms
4. **Intelligent Routing**: 
   - 5-star reviews redirected to Google Business Profile
   - Lower ratings kept internal for business owner response
5. **Response Management**: Business owners can respond to internal reviews

## External Dependencies

### Email Service
- Gmail SMTP integration (currently in development mode - logs emails instead of sending)
- Configured for production Gmail API or alternative email services like SendGrid

### Frontend Libraries
- Bootstrap 5 (via CDN)
- Font Awesome 6.4.0 (via CDN)
- Custom CSS for enhanced styling

### Python Packages
- Flask and Flask extensions (SQLAlchemy, Login, WTF)
- Werkzeug for security utilities
- WTForms for form handling

## Deployment Strategy

### Development Environment
- SQLite database for local development
- Flask development server with debug mode
- Environment variables for configuration

### Production Considerations
- PostgreSQL database support via DATABASE_URL environment variable
- ProxyFix middleware for proper header handling behind reverse proxies
- Session secret key via SESSION_SECRET environment variable
- Email service credentials via GMAIL_USER/GMAIL_PASSWORD environment variables

### Configuration Management
- Environment-based configuration (development vs production)
- Database connection pooling with automatic reconnection
- Logging configuration for debugging and monitoring

The application follows a traditional MVC pattern with clear separation of concerns between models (data), views (templates), and controllers (routes). The codebase is structured for scalability and includes proper error handling, form validation, and user experience enhancements.