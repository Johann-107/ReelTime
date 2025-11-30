# accounts/sendgrid_utils.py
import logging
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To

logger = logging.getLogger(__name__)

def send_sendgrid_email(to_email, subject, plain_text_content, html_content=None):
    """
    Send email using SendGrid Web API
    """
    try:
        # Check if SendGrid is configured
        if not settings.SENDGRID_API_KEY:
            print("🔴 SendGrid API key not configured")
            logger.error("SendGrid API key not configured")
            return False
            
        # Initialize SendGrid client
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        
        # Create Mail object
        from_email = settings.SENDGRID_SENDER_EMAIL
        to_emails = [To(email=to_email)]
        
        message = Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=subject,
            plain_text_content=plain_text_content,
            html_content=html_content
        )
        
        # Send email
        response = sg.send(message)
        
        if response.status_code in [200, 202]:
            print(f"🟢 SendGrid: Email sent successfully to {to_email}, Status: {response.status_code}")
            return True
        else:
            print(f"🔴 SendGrid: Failed to send email, Status: {response.status_code}, Body: {response.body}")
            logger.error(f"SendGrid API error: {response.status_code} - {response.body}")
            return False
            
    except Exception as e:
        print(f"🔴 SendGrid: Exception occurred: {e}")
        logger.error(f"SendGrid exception: {e}")
        return False