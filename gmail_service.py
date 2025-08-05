import os
import smtplib
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

def send_review_request_email(to_email, subject, message_template, customer_name, business_name, review_link):
    """
    Send a review request email to a customer.
    In development mode, emails are logged instead of sent.
    In production, configure Gmail SMTP credentials.
    """
    try:
        # Format the message with variables
        formatted_message = message_template.format(
            customer_name=customer_name,
            business_name=business_name,
            review_link=review_link
        )
        
        # For development, just log the email instead of sending
        logger.info(f"Review request email would be sent to: {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Message: {formatted_message}")
        logger.info(f"Review link: {review_link}")
        
        # In production, you would uncomment and configure the SMTP sending:
        # gmail_user = os.environ.get('GMAIL_USER')
        # gmail_password = os.environ.get('GMAIL_PASSWORD')
        # 
        # if gmail_user and gmail_password:
        #     msg = MIMEText(formatted_message)
        #     msg['Subject'] = subject
        #     msg['From'] = gmail_user
        #     msg['To'] = to_email
        #     
        #     server = smtplib.SMTP('smtp.gmail.com', 587)
        #     server.starttls()
        #     server.login(gmail_user, gmail_password)
        #     server.send_message(msg)
        #     server.quit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error with email process: {str(e)}")
        return False

def send_admin_notification(admin_email, customer_name, rating, comment):
    """
    Send notification to admin about a low-rating review
    In development mode, notifications are logged instead of sent.
    """
    try:
        logger.info(f"Admin notification would be sent to: {admin_email}")
        logger.info(f"Low rating alert: {rating} stars from {customer_name}")
        logger.info(f"Comment: {comment}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error with admin notification: {str(e)}")
        return False

def send_email(to_email, subject, message, user_id=None, attachment_path=None):
    """
    Generic email sending function for automation features
    """
    try:
        # Create message with proper headers
        msg = MIMEMultipart()
        gmail_user = os.environ.get('GMAIL_USER')
        
        # Get business name from user if provided
        business_name = "Review Automation Platform"
        if user_id:
            from models import User
            user = User.query.get(user_id)
            if user and user.business_name:
                business_name = user.business_name
        
        msg['From'] = f"{business_name} <{gmail_user}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Reply-To'] = gmail_user
        
        # Add headers
        msg['Message-ID'] = f"<{uuid.uuid4()}@{gmail_user.split('@')[1] if gmail_user else 'localhost'}>"
        msg['Date'] = formatdate(localtime=True)
        
        # Create HTML version
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <p>{message.replace(chr(10), '<br>')}</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">
                    This email was sent from {business_name}.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Add both versions
        msg.attach(MIMEText(message, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment:
                from email.mime.base import MIMEBase
                from email import encoders
                
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                msg.attach(part)
        
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        gmail_password = os.environ.get('GMAIL_PASSWORD')
        
        if not gmail_user or not gmail_password:
            logger.warning("Gmail credentials not configured - email not sent")
            return False
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False
