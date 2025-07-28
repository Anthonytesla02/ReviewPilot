# AI-Assisted Review Automation Platform

A comprehensive Flask-based business review management system that automates customer review collection and intelligently routes feedback to maximize positive Google reviews while capturing actionable insights from lower ratings.

## 🌟 Key Features

### Smart Review Routing
- **1-3 Stars**: Detailed feedback form with specific issue categories
- **4 Stars**: Admin notification for improvement opportunities  
- **5 Stars**: Auto-redirect to Google Reviews with countdown timer

### Professional Email System
- Anti-spam HTML email templates with proper headers
- Real-time Gmail SMTP integration
- Automated review request campaigns
- Admin notifications for all feedback

### Customer Management
- Complete customer database with appointment tracking
- Bulk review request sending
- Customer interaction history
- Service type categorization

### Analytics & Insights
- Review performance dashboard
- Customer feedback analysis
- Rating distribution tracking
- Response time monitoring

## 🚀 Quick Start

### Environment Variables
Set these in your deployment platform:

```bash
DATABASE_URL=your_postgresql_database_url
SESSION_SECRET=your_secure_random_secret_key
GMAIL_USER=your_gmail_address@gmail.com
GMAIL_PASSWORD=your_gmail_app_password
```

### Gmail Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Google Account > Security > App passwords
3. Use the App Password (not your regular password) for GMAIL_PASSWORD

## 📋 Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: Bootstrap 5, Jinja2 templates, JavaScript
- **Email**: Gmail SMTP with HTML templates
- **Deployment**: Vercel-ready with configuration files

## 🎯 Business Value

### For Business Owners
- Increase Google review quantity and quality
- Identify improvement opportunities from 4-star feedback
- Address customer concerns before they become public
- Professional automated communication

### For Customers  
- Easy-to-use review interface with visual star ratings
- Constructive feedback channels for concerns
- Seamless experience across all rating levels
- Mobile-responsive design

## 🏗️ Architecture

### Smart Routing Logic
```
Customer Review → Rating Analysis:
├── 1-3 Stars → Detailed Feedback Form → Internal Handling
├── 4 Stars → Admin Alert → Improvement Opportunity  
└── 5 Stars → Google Review Redirect → Public Visibility
```

### Security Features
- CSRF protection on all forms
- Secure session management
- Password hashing with Werkzeug
- Environment-based configuration
- SQL injection prevention

## 📱 User Experience

### Review Form Features
- Interactive star rating with hover effects
- Progressive disclosure (rating first, then comment)
- Professional branding integration
- Mobile-optimized interface

### Admin Dashboard
- Real-time review monitoring
- Customer management tools
- Email template customization
- Analytics and reporting

## 🔧 Development

### Local Setup
```bash
git clone [repository-url]
cd review-automation-platform
# Set environment variables
flask run
```

### Database Migrations
The app automatically creates tables on startup. For schema changes in production, use database migration tools.

## 🌐 Deployment

### Vercel (Recommended)
- Automatic detection of Flask app
- Built-in PostgreSQL database options
- Environment variable management
- Global CDN and SSL included

### Other Platforms
Compatible with Railway, Heroku, DigitalOcean, and any Python hosting service that supports Flask.

## 📊 Performance

- Database connection pooling for scalability
- Optimized queries with SQLAlchemy ORM
- Responsive design for all device types
- Professional email delivery rates

## 🎨 Customization

### Email Templates
- Customizable HTML email designs
- Variable substitution (customer name, business name, review link)
- Professional formatting with anti-spam headers

### Branding
- Business name integration throughout interface
- Customizable Google Business Profile links
- Professional styling with Bootstrap themes

---

Built with ❤️ for businesses who care about customer feedback and online reputation management.