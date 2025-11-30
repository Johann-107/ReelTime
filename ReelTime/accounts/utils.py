# accounts/utils.py
from .models import User
import re
import logging
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .sendgrid_utils import send_sendgrid_email

logger = logging.getLogger(__name__)

def create_default_admin(cinema_name, email):
    # Convert to lowercase, replace spaces with underscores, remove invalid chars
    safe_cinema_name = re.sub(r'[^a-z0-9_]+', '', cinema_name.lower().replace(' ', '_'))

    admin = User.objects.create(
        first_name='Cinema',
        last_name='Admin',
        username=f"{safe_cinema_name}_admin",
        email=email,
        phone_number="00000000000",
        password=make_password('admin123'),
        is_admin=True,
        must_change_password=True,
        cinema_name=cinema_name
    )
    return admin

def get_logged_in_user(request):
    user_id = request.session.get('user_id')
    return User.objects.filter(id=user_id).first()

# Email sending functions using SendGrid (synchronous)
def send_admin_confirmation_email(email, confirmation_link, cinema_name):
    """Send admin confirmation email using SendGrid"""
    try:
        print(f"🟡 Sending admin confirmation email to {email}")
        
        subject = "Confirm your admin registration - ReelTime"
        
        # Plain text content
        plain_text_message = (
            f"Hello!\n\n"
            f"Did you register as admin for '{cinema_name}' on ReelTime?\n\n"
            f"If yes, please confirm by clicking this link:\n{confirmation_link}\n\n"
            f"If not, you can ignore this email.\n\n"
            f"Best regards,\nReelTime Team"
        )
        
        # HTML content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Confirm Your Admin Registration</h1>
            </div>
            <div class="content">
                <p>Hello!</p>
                <p>Did you register as admin for <strong>{cinema_name}</strong> on ReelTime?</p>
                <p>If yes, please confirm by clicking the button below:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{confirmation_link}" class="button">Confirm Admin Registration</a>
                </p>
                <p>If not, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>Best regards,<br>ReelTime Team</p>
            </div>
        </body>
        </html>
        """
        
        # Send email using SendGrid
        success = send_sendgrid_email(
            to_email=email,
            subject=subject,
            plain_text_content=plain_text_message,
            html_content=html_message
        )
        
        if success:
            print(f"🟢 Admin confirmation email sent successfully to {email}")
        else:
            print(f"🔴 Failed to send admin confirmation email to {email}")
            
        return success
        
    except Exception as e:
        print(f"🔴 Error sending admin confirmation email to {email}: {e}")
        logger.error(f"Error sending admin confirmation email to {email}: {e}")
        return False

def send_admin_credentials_email(email, cinema_name, username):
    """Send admin credentials email using SendGrid"""
    try:
        print(f"🟡 Sending admin credentials email to {email}")
        
        subject = "Your ReelTime Admin Account Credentials"
        
        # Plain text content
        plain_text_message = (
            f"Your admin account for '{cinema_name}' has been created!\n\n"
            f"📋 Account Details:\n"
            f"Cinema: {cinema_name}\n"
            f"Username: {username}\n"
            f"Password: admin123\n\n"
            f"🔐 Important Security Notice:\n"
            f"Please log in immediately and change your password.\n"
            f"For security reasons, do not share these credentials with anyone.\n\n"
            f"Best regards,\nReelTime Team"
        )
        
        # HTML content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .credentials {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #28a745; }}
                .security {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ffc107; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Admin Account Created Successfully!</h1>
            </div>
            <div class="content">
                <p>Your admin account for <strong>{cinema_name}</strong> has been created!</p>
                
                <div class="credentials">
                    <h3>📋 Account Details:</h3>
                    <p><strong>Cinema:</strong> {cinema_name}</p>
                    <p><strong>Username:</strong> {username}</p>
                    <p><strong>Password:</strong> admin123</p>
                </div>
                
                <div class="security">
                    <h3>🔐 Important Security Notice:</h3>
                    <p>Please log in immediately and change your password.</p>
                    <p>For security reasons, do not share these credentials with anyone.</p>
                </div>
            </div>
            <div class="footer">
                <p>Best regards,<br><strong>ReelTime Team</strong></p>
            </div>
        </body>
        </html>
        """
        
        # Send email using SendGrid
        success = send_sendgrid_email(
            to_email=email,
            subject=subject,
            plain_text_content=plain_text_message,
            html_content=html_message
        )
        
        if success:
            print(f"🟢 Admin credentials email sent successfully to {email}")
        else:
            print(f"🔴 Failed to send admin credentials email to {email}")
            
        return success
        
    except Exception as e:
        print(f"🔴 Error sending admin credentials email to {email}: {e}")
        logger.error(f"Error sending admin credentials email to {email}: {e}")
        return False