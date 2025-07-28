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
        
        # Create message with proper headers to avoid spam
        msg = MIMEMultipart('alternative')
        gmail_user = os.environ.get('GMAIL_USER')
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
