import os
import json
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from collections import Counter

from app import db
from models import User, Customer, Review

def generate_pdf_report(user_id: int, report_type: str = 'weekly') -> str:
    """Generate PDF report for user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Calculate date range
        end_date = datetime.utcnow()
        if report_type == 'weekly':
            start_date = end_date - timedelta(days=7)
            period_name = "Weekly"
        else:  # monthly
            start_date = end_date - timedelta(days=30)
            period_name = "Monthly"
        
        # Create reports directory if it doesn't exist
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{reports_dir}/{user.username}_{report_type}_report_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12
        )
        
        # Content
        story = []
        
        # Title
        business_name = user.business_name or user.username
        title = f"{period_name} Review Report - {business_name}"
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Report period
        period_text = f"Report Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(period_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Get data for the period
        reviews = Review.query.filter(
            Review.user_id == user_id,
            Review.created_at >= start_date,
            Review.created_at <= end_date
        ).all()
        
        customers = Customer.query.filter(
            Customer.user_id == user_id,
            Customer.created_at >= start_date,
            Customer.created_at <= end_date
        ).count()
        
        # Summary Statistics
        story.append(Paragraph("Summary Statistics", heading_style))
        
        total_reviews = len(reviews)
        avg_rating = sum(r.rating for r in reviews) / total_reviews if total_reviews > 0 else 0
        rating_distribution = Counter(r.rating for r in reviews)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Reviews', str(total_reviews)],
            ['Average Rating', f"{avg_rating:.1f}/5.0"],
            ['New Customers', str(customers)],
            ['5-Star Reviews', str(rating_distribution.get(5, 0))],
            ['4-Star Reviews', str(rating_distribution.get(4, 0))],
            ['3-Star Reviews', str(rating_distribution.get(3, 0))],
            ['2-Star Reviews', str(rating_distribution.get(2, 0))],
            ['1-Star Reviews', str(rating_distribution.get(1, 0))],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Sentiment Analysis (if available)
        sentiment_counts = Counter(r.sentiment for r in reviews if r.sentiment)
        if sentiment_counts:
            story.append(Paragraph("Sentiment Analysis", heading_style))
            
            sentiment_data = [['Sentiment', 'Count']]
            for sentiment, count in sentiment_counts.most_common():
                sentiment_data.append([sentiment.title(), str(count)])
            
            sentiment_table = Table(sentiment_data, colWidths=[3*inch, 2*inch])
            sentiment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(sentiment_table)
            story.append(Spacer(1, 20))
        
        # Recent Reviews
        if reviews:
            story.append(Paragraph("Recent Reviews", heading_style))
            
            for review in reviews[-5:]:  # Last 5 reviews
                review_text = f"<b>{review.rating}/5 stars</b> - {review.customer.name}"
                if review.comment:
                    review_text += f"<br/><i>\"{review.comment[:100]}{'...' if len(review.comment) > 100 else ''}\"</i>"
                if review.sentiment:
                    review_text += f"<br/>Sentiment: {review.sentiment.title()}"
                
                story.append(Paragraph(review_text, styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Issues requiring attention
        pending_reviews = Review.query.filter(
            Review.user_id == user_id,
            Review.rating <= 3,
            Review.status == 'pending'
        ).all()
        
        if pending_reviews:
            story.append(Paragraph("Reviews Requiring Attention", heading_style))
            for review in pending_reviews:
                issue_text = f"<b>{review.rating}/5 stars</b> from {review.customer.name} - {review.created_at.strftime('%B %d, %Y')}"
                if review.comment:
                    issue_text += f"<br/>\"{review.comment[:150]}{'...' if len(review.comment) > 150 else ''}\""
                
                story.append(Paragraph(issue_text, styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        
        return filename
        
    except Exception as e:
        print(f"Error generating report: {e}")
        return None