import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def send_review_request_email(to_email, subject, message_template, customer_name, business_name, review_link):
    """
    Send a review request email to a customer.
    This function uses SMTP with Gmail. In production, you would configure
    Gmail API credentials or use a service like SendGrid.
    """
    try:
        # Format the message with variables
        formatted_message = message_template.format(
            customer_name=customer_name,
            business_name=business_name,
            review_link=review_link
        )
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = os.environ.get('GMAIL_USER', 'noreply@example.com')
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(formatted_message, 'plain'))
        
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        gmail_user = os.environ.get('GMAIL_USER')
        gmail_password = os.environ.get('GMAIL_PASSWORD')  # Use app password
        
        if not gmail_user or not gmail_password:
            logger.error("Gmail credentials not configured. Please set GMAIL_USER and GMAIL_PASSWORD environment variables.")
            raise Exception("Gmail credentials not configured")
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(gmail_user, gmail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email} with subject: {subject}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise e

def send_admin_notification(admin_email, customer_name, rating, comment):
    """
    Send notification to admin about a low-rating review
    """
    try:
        subject = f"Low Rating Alert - {rating} stars from {customer_name}"
        message = f"""
        You have received a {rating}-star review from {customer_name}.
        
        Comment: {comment}
        
        Please log into your dashboard to respond to this review.
        """
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = os.environ.get('GMAIL_USER', 'noreply@example.com')
        msg['To'] = admin_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(message, 'plain'))
        
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        gmail_user = os.environ.get('GMAIL_USER')
        gmail_password = os.environ.get('GMAIL_PASSWORD')
        
        if not gmail_user or not gmail_password:
            logger.error("Gmail credentials not configured for admin notification")
            return False
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(gmail_user, gmail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, admin_email, text)
        server.quit()
        
        logger.info(f"Admin notification sent successfully to {admin_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending admin notification: {str(e)}")
        return False
