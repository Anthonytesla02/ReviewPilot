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
        
        # For production, you would use actual Gmail SMTP with proper credentials
        # Here we'll log the email instead of actually sending it
        logger.info(f"""
        EMAIL WOULD BE SENT:
        To: {to_email}
        Subject: {subject}
        Message: {formatted_message}
        """)
        
        # In a real application, uncomment and configure the following:
        """
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        gmail_user = os.environ.get('GMAIL_USER')
        gmail_password = os.environ.get('GMAIL_PASSWORD')  # Use app password
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(gmail_user, gmail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, to_email, text)
        server.quit()
        """
        
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
        
        # Log instead of actually sending
        logger.info(f"""
        ADMIN NOTIFICATION WOULD BE SENT:
        To: {admin_email}
        Subject: {subject}
        Message: {message}
        """)
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending admin notification: {str(e)}")
        return False
