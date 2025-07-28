from flask import url_for
import logging

logger = logging.getLogger(__name__)

def generate_review_link(token):
    """Generate a public review link for the given token"""
    return url_for('public_review', token=token, _external=True)

def format_date(date):
    """Format datetime for display"""
    if date:
        return date.strftime('%B %d, %Y at %I:%M %p')
    return 'Not set'

def get_rating_color(rating):
    """Get Bootstrap color class based on rating"""
    if rating >= 5:
        return 'success'
    elif rating >= 4:
        return 'primary'
    elif rating >= 3:
        return 'warning'
    else:
        return 'danger'

def get_status_color(status):
    """Get Bootstrap color class based on status"""
    status_colors = {
        'pending': 'warning',
        'responded': 'success',
        'forwarded_to_google': 'primary',
        'sent': 'info',
        'opened': 'primary',
        'completed': 'success',
        'failed': 'danger'
    }
    return status_colors.get(status, 'secondary')

def calculate_review_stats(reviews):
    """Calculate review statistics"""
    if not reviews:
        return {
            'total': 0,
            'average': 0,
            'distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
    
    total = len(reviews)
    total_rating = sum(review.rating for review in reviews)
    average = round(total_rating / total, 1) if total > 0 else 0
    
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        distribution[review.rating] += 1
    
    return {
        'total': total,
        'average': average,
        'distribution': distribution
    }
