import random
import string
import threading
import re
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password

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

# Email sending functions with threading
def send_admin_confirmation_email(email, confirmation_link, cinema_name):
    """Send admin confirmation email in a thread"""
    try:
        email_thread = threading.Thread(
            target=_send_admin_confirmation_email_thread,
            args=(email, confirmation_link, cinema_name)
        )
        email_thread.daemon = True
        email_thread.start()
        print(f"🟡 Admin confirmation email thread started for {email}")
        return True
    except Exception as e:
        print(f"🔴 Failed to start admin confirmation email thread: {e}")
        logger.error(f"Failed to start admin confirmation email thread for {email}: {e}")
        return False

def _send_admin_confirmation_email_thread(email, confirmation_link, cinema_name):
    """Thread function to send admin confirmation email"""
    try:
        print(f"🟡 Thread: Sending admin confirmation email to {email}")
        
        subject = "Confirm your admin registration - ReelTime"
        message = (
            f"Hello!\n\n"
            f"Did you register as admin for '{cinema_name}' on ReelTime?\n\n"
            f"If yes, please confirm by clicking this link:\n{confirmation_link}\n\n"
            f"If not, you can ignore this email.\n\n"
            f"Best regards,\nReelTime Team"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        print(f"🟢 Thread: Admin confirmation email sent successfully to {email}")
        
    except Exception as e:
        print(f"🔴 Thread: Error sending admin confirmation email to {email}: {e}")
        logger.error(f"Error sending admin confirmation email to {email}: {e}")

def send_admin_credentials_email(email, cinema_name, username):
    """Send admin credentials email in a thread"""
    try:
        email_thread = threading.Thread(
            target=_send_admin_credentials_email_thread,
            args=(email, cinema_name, username)
        )
        email_thread.daemon = True
        email_thread.start()
        print(f"🟡 Admin credentials email thread started for {email}")
        return True
    except Exception as e:
        print(f"🔴 Failed to start admin credentials email thread: {e}")
        logger.error(f"Failed to start admin credentials email thread for {email}: {e}")
        return False

def _send_admin_credentials_email_thread(email, cinema_name, username):
    """Thread function to send admin credentials email"""
    try:
        print(f"🟡 Thread: Sending admin credentials email to {email}")
        
        subject = "Your ReelTime Admin Account Credentials"
        message = (
            f"Your admin account for '{cinema_name}' has been created!\n\n"
            f"📋 Account Details:\n"
            f"Cinema: {cinema_name}\n"
            f"Username: {username}\n"
            f"Password: admin123\n\n"
            f"🔐 Important Security Notice:\n"
            f"Please log in immediately and change your password.\n"
            f"Login URL: {settings.BASE_URL}/accounts/login/\n\n"
            f"For security reasons, do not share these credentials with anyone.\n\n"
            f"Best regards,\nReelTime Team"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        print(f"🟢 Thread: Admin credentials email sent successfully to {email}")
        
    except Exception as e:
        print(f"🔴 Thread: Error sending admin credentials email to {email}: {e}")
        logger.error(f"Error sending admin credentials email to {email}: {e}")

# Enhanced email sending with retry logic
class AccountsEmailThread(threading.Thread):
    """
    Enhanced email thread for accounts with error handling and retry logic
    """
    def __init__(self, email_function, *args, max_retries=3):
        threading.Thread.__init__(self)
        self.email_function = email_function
        self.args = args
        self.max_retries = max_retries
        self.daemon = True
        
    def run(self):
        retries = 0
        while retries < self.max_retries:
            try:
                self.email_function(*self.args)
                break  # Success, exit retry loop
            except Exception as e:
                retries += 1
                if retries < self.max_retries:
                    print(f"🟡 Accounts email retry {retries}/{self.max_retries}")
                    import time
                    time.sleep(2 ** retries)  # Exponential backoff
                else:
                    print(f"🔴 All account email retries failed: {e}")
                    logger.error(f"All account email retries failed: {e}")

# Enhanced email sending functions
def send_admin_confirmation_email_enhanced(email, confirmation_link, cinema_name):
    """Enhanced version with retry logic"""
    email_thread = AccountsEmailThread(
        _send_admin_confirmation_email_thread, 
        email, confirmation_link, cinema_name
    )
    email_thread.start()

def send_admin_credentials_email_enhanced(email, cinema_name, username):
    """Enhanced version with retry logic"""
    email_thread = AccountsEmailThread(
        _send_admin_credentials_email_thread,
        email, cinema_name, username
    )
    email_thread.start()