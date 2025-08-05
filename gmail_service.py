import os
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
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
        
        # Check Gmail credentials first
        gmail_user = os.environ.get('GMAIL_USER')
        gmail_password = os.environ.get('GMAIL_PASSWORD')
        
        if not gmail_user or not gmail_password:
            logger.error("Gmail credentials not configured. Email will be logged instead of sent.")
            logger.info(f"Would send email to {to_email}:")
            logger.info(f"Subject: {subject}")
            logger.info(f"Message: {formatted_message}")
            return True  # Return success for development mode
        
        # Create message with proper headers to avoid spam
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{business_name} <{gmail_user}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Reply-To'] = gmail_user
        
        # Add headers to improve deliverability
        msg['Message-ID'] = f"<{uuid.uuid4()}@{gmail_user.split('@')[1]}>"
        msg['Date'] = formatdate(localtime=True)
        msg['X-Mailer'] = 'ReviewPro Business Platform'
        
        # Create both plain text and HTML versions
        text_body = formatted_message
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">Thank you for choosing {business_name}!</h2>
                <p>{formatted_message.replace(chr(10), '<br>')}</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{review_link}" 
                       style="background-color: #2c5aa0; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;
                              font-weight: bold;">Leave Your Review</a>
                </div>
                <p style="font-size: 12px; color: #666; margin-top: 30px;">
                    This email was sent from {business_name}. If you have any questions, 
                    please reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Add both versions
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
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
