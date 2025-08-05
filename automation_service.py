import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from flask import current_app
import schedule
import time
from threading import Thread

from app import db
from models import (
    User, Customer, Review, ReviewConversation, FollowUpSequence, 
    Referral, AutomationSettings, ReportGeneration
)
from ai_service import mistral_service
from gmail_service import send_email
from report_generator import generate_pdf_report

logger = logging.getLogger(__name__)

class AutomationService:
    """Service class for handling automation workflows"""
    
    @staticmethod
    def process_new_review(review_id: int):
        """Process a newly submitted review with AI analysis"""
        try:
            review = Review.query.get(review_id)
            if not review or not review.comment:
                return
            
            # Analyze sentiment
            sentiment, score = mistral_service.analyze_sentiment(review.comment)
            review.sentiment = sentiment
            review.sentiment_score = score
            
            # Categorize feedback
            review.review_category = mistral_service.categorize_feedback(review.comment)
            
            # Generate AI suggestion if enabled
            user_settings = AutomationSettings.query.filter_by(user_id=review.user_id).first()
            if user_settings and user_settings.ai_auto_reply_enabled:
                suggestion = mistral_service.generate_response_suggestion(
                    review.comment,
                    review.rating,
                    review.user.business_name or "our business",
                    user_settings.ai_tone
                )
                review.ai_suggested_response = suggestion
            
            # For 5-star reviews, trigger referral system
            if review.rating == 5:
                AutomationService.trigger_referral_reward(review.customer_id)
            
            db.session.commit()
            logger.info(f"Processed review {review_id} with sentiment: {sentiment}")
            
        except Exception as e:
            logger.error(f"Error processing review {review_id}: {e}")
            db.session.rollback()
    
    @staticmethod
    def send_ai_response(review_id: int, custom_message: str = None):
        """Send AI-generated or custom response to customer"""
        try:
            review = Review.query.get(review_id)
            if not review:
                return False
            
            message = custom_message or review.ai_suggested_response
            if not message:
                return False
            
            # Send email response
            subject = f"Thank you for your review - {review.user.business_name}"
            success = send_email(
                to_email=review.customer.email,
                subject=subject,
                message=message,
                user_id=review.user_id
            )
            
            if success:
                # Log in conversation history
                conversation = ReviewConversation(
                    review_id=review_id,
                    message=message,
                    sender='ai' if not custom_message else 'admin',
                    is_ai_generated=not bool(custom_message)
                )
                db.session.add(conversation)
                
                # Update review status
                review.admin_response = message
                review.response_date = datetime.utcnow()
                review.status = 'responded'
                
                db.session.commit()
                return True
            
        except Exception as e:
            logger.error(f"Error sending AI response for review {review_id}: {e}")
            db.session.rollback()
        
        return False
    
    @staticmethod
    def schedule_follow_ups(customer_id: int):
        """Schedule follow-up email sequence for customer"""
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                return
            
            # Check if customer already has pending follow-ups
            existing = FollowUpSequence.query.filter_by(
                customer_id=customer_id,
                status='scheduled'
            ).first()
            if existing:
                return
            
            settings = AutomationSettings.query.filter_by(user_id=customer.user_id).first()
            if not settings or not settings.follow_up_enabled:
                return
            
            # Schedule 3-step sequence
            delays = [settings.follow_up_delay_1, settings.follow_up_delay_2, settings.follow_up_delay_3]
            messages = [settings.follow_up_message_1, settings.follow_up_message_2, settings.follow_up_message_3]
            
            for step, (delay, message) in enumerate(zip(delays, messages), 1):
                if delay and delay > 0:
                    scheduled_time = datetime.utcnow() + timedelta(days=delay)
                    
                    follow_up = FollowUpSequence(
                        user_id=customer.user_id,
                        customer_id=customer_id,
                        sequence_step=step,
                        scheduled_for=scheduled_time,
                        email_content=message
                    )
                    db.session.add(follow_up)
            
            db.session.commit()
            logger.info(f"Scheduled follow-ups for customer {customer_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling follow-ups for customer {customer_id}: {e}")
            db.session.rollback()
    
    @staticmethod
    def process_pending_follow_ups():
        """Process and send pending follow-up emails"""
        try:
            now = datetime.utcnow()
            pending_follow_ups = FollowUpSequence.query.filter(
                FollowUpSequence.status == 'scheduled',
                FollowUpSequence.scheduled_for <= now
            ).all()
            
            for follow_up in pending_follow_ups:
                # Check if customer has already submitted a review
                recent_review = Review.query.filter_by(
                    customer_id=follow_up.customer_id
                ).filter(Review.created_at >= follow_up.scheduled_for - timedelta(days=1)).first()
                
                if recent_review:
                    # Cancel remaining follow-ups
                    FollowUpSequence.query.filter_by(
                        customer_id=follow_up.customer_id,
                        status='scheduled'
                    ).update({'status': 'cancelled'})
                    db.session.commit()
                    continue
                
                # Generate email content if not provided
                email_content = follow_up.email_content
                if not email_content:
                    settings = AutomationSettings.query.filter_by(user_id=follow_up.user_id).first()
                    incentive = settings.referral_reward_value if settings and follow_up.sequence_step == 3 else None
                    
                    email_data = mistral_service.generate_follow_up_email(
                        follow_up.customer.name,
                        follow_up.customer.user.business_name or "our business",
                        follow_up.sequence_step,
                        incentive
                    )
                    email_content = email_data['body']
                    subject = email_data['subject']
                else:
                    subject = f"Reminder - Share your experience"
                
                # Send email
                success = send_email(
                    to_email=follow_up.customer.email,
                    subject=subject,
                    message=email_content,
                    user_id=follow_up.user_id
                )
                
                if success:
                    follow_up.sent_at = datetime.utcnow()
                    follow_up.status = 'sent'
                    follow_up.email_content = email_content
                
                db.session.commit()
            
        except Exception as e:
            logger.error(f"Error processing follow-ups: {e}")
            db.session.rollback()
    
    @staticmethod
    def trigger_referral_reward(customer_id: int):
        """Trigger referral reward for 5-star review customer"""
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                return
            
            settings = AutomationSettings.query.filter_by(user_id=customer.user_id).first()
            if not settings or not settings.referral_reward_enabled:
                return
            
            # Generate unique referral token
            referral_token = str(uuid.uuid4())[:8].upper()
            
            referral = Referral(
                user_id=customer.user_id,
                customer_id=customer_id,
                referral_token=referral_token
            )
            db.session.add(referral)
            
            # Send thank you email with referral link
            business_name = customer.user.business_name or "our business"
            reward_value = settings.referral_reward_value or "10% off next service"
            
            referral_link = f"{current_app.config.get('SERVER_NAME', 'your-domain.com')}/referral/{referral_token}"
            
            email_content = f"""Dear {customer.name},

Thank you so much for your 5-star review! We're thrilled that you had such a positive experience with {business_name}.

As a token of our appreciation, we'd like to offer you {reward_value} and invite you to share {business_name} with friends and family.

Your personal referral link: {referral_link}

When someone books through your link, they'll receive a special welcome offer, and you'll get additional rewards!

Thank you again for your support.

Best regards,
{business_name} Team"""

            send_email(
                to_email=customer.email,
                subject=f"Thank you for your 5-star review! + Exclusive referral rewards",
                message=email_content,
                user_id=customer.user_id
            )
            
            db.session.commit()
            logger.info(f"Created referral {referral_token} for customer {customer_id}")
            
        except Exception as e:
            logger.error(f"Error creating referral for customer {customer_id}: {e}")
            db.session.rollback()
    
    @staticmethod
    def generate_and_send_reports():
        """Generate and send scheduled reports"""
        try:
            # Find users with report settings
            users_with_reports = User.query.join(AutomationSettings).filter(
                AutomationSettings.report_recipients.isnot(None)
            ).all()
            
            for user in users_with_reports:
                settings = user.automation_settings
                if not settings.report_recipients:
                    continue
                
                # Check if report is due
                last_report = ReportGeneration.query.filter_by(
                    user_id=user.id,
                    report_type=settings.report_frequency
                ).order_by(ReportGeneration.generated_at.desc()).first()
                
                days_since_last = 999
                if last_report:
                    days_since_last = (datetime.utcnow() - last_report.generated_at).days
                
                should_generate = False
                if settings.report_frequency == 'weekly' and days_since_last >= 7:
                    should_generate = True
                elif settings.report_frequency == 'monthly' and days_since_last >= 30:
                    should_generate = True
                
                if should_generate:
                    # Generate report
                    report_path = generate_pdf_report(user.id, settings.report_frequency)
                    if report_path:
                        # Send to recipients
                        recipients = json.loads(settings.report_recipients)
                        for email in recipients:
                            send_email(
                                to_email=email,
                                subject=f"{settings.report_frequency.title()} Review Report - {user.business_name}",
                                message=f"Please find attached your {settings.report_frequency} review report.",
                                user_id=user.id,
                                attachment_path=report_path
                            )
                        
                        # Log report generation
                        report_record = ReportGeneration(
                            user_id=user.id,
                            report_type=settings.report_frequency,
                            file_path=report_path,
                            sent_to=settings.report_recipients
                        )
                        db.session.add(report_record)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            db.session.rollback()

def start_automation_scheduler():
    """Start the background scheduler for automation tasks"""
    def run_scheduler():
        schedule.every(10).minutes.do(AutomationService.process_pending_follow_ups)
        schedule.every().day.at("09:00").do(AutomationService.generate_and_send_reports)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    # Start scheduler in background thread
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Automation scheduler started")

# Initialize scheduler on import (but not in Vercel serverless environment)
if (os.environ.get('FLASK_ENV') != 'testing' and 
    not os.environ.get('VERCEL') and 
    not os.environ.get('VERCEL_ENV')):
    start_automation_scheduler()