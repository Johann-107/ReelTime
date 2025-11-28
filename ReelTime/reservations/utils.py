import threading
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_reservation_confirmation_email(reservation_id):
    """
    Send reservation confirmation email in a thread
    """
    from .models import Reservation
    
    try:
        print(f"🟡 Thread: Sending confirmation email for reservation {reservation_id}")
        reservation = Reservation.objects.get(id=reservation_id)
        user = reservation.user
        
        subject = f"🎬 Reservation Confirmed - {reservation.movie_detail.movie.title}"
        
        message = (
            f"Hello {user.first_name or user.username},\n\n"
            f"Your movie reservation has been confirmed!\n\n"
            f"📋 Reservation Details:\n"
            f"Movie: {reservation.movie_detail.movie.title}\n"
            f"Cinema: {reservation.cinema_name}\n"
            f"Date: {reservation.selected_date}\n"
            f"Showtime: {reservation.selected_showtime}\n"
            f"Number of Seats: {reservation.number_of_seats}\n"
            f"Seats: {', '.join(reservation.selected_seats) if reservation.selected_seats else 'Not specified'}\n"
            f"Total Cost: ${reservation.total_cost}\n"
            f"Reservation ID: {reservation.id}\n\n"
            f"We look forward to seeing you at the cinema!\n\n"
            f"Thank you for choosing ReelTime!"
        )
        
        print(f"🟡 Thread: Sending email to {user.email}")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        # Update confirmation sent status
        reservation.confirmation_sent = True
        reservation.save(update_fields=['confirmation_sent'])
        
        print(f"🟢 Thread: Confirmation email sent successfully for reservation {reservation_id}")
        
    except Reservation.DoesNotExist:
        print(f"🔴 Thread: Reservation {reservation_id} not found")
        logger.error(f"Reservation {reservation_id} not found for confirmation email")
    except Exception as e:
        print(f"🔴 Thread: Error sending confirmation email: {e}")
        logger.error(f"Error sending confirmation email for reservation {reservation_id}: {e}")

def send_reservation_reminder_email(reservation_id):
    """
    Send reservation reminder email in a thread
    """
    from .models import Reservation
    
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        user = reservation.user
        
        subject = f"⏰ Movie Reminder - {reservation.movie_detail.movie.title} tomorrow!"
        
        message = (
            f"Hello {user.first_name or user.username},\n\n"
            f"This is a friendly reminder about your movie reservation tomorrow!\n\n"
            f"🎟️ Your Reservation:\n"
            f"Movie: {reservation.movie_detail.movie.title}\n"
            f"Cinema: {reservation.cinema_name}\n"
            f"Date: {reservation.selected_date}\n"
            f"Showtime: {reservation.selected_showtime}\n"
            f"Seats: {', '.join(reservation.selected_seats) if reservation.selected_seats else 'Not specified'}\n\n"
            f"Please arrive at least 15 minutes before the showtime.\n\n"
            f"Enjoy your movie experience! 🍿"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        # Update reminder sent status
        reservation.reminder_sent = True
        reservation.save(update_fields=['reminder_sent'])
        
        print(f"🟢 Thread: Reminder email sent successfully for reservation {reservation_id}")
        
    except Exception as e:
        print(f"🔴 Thread: Error sending reminder email: {e}")
        logger.error(f"Error sending reminder email for reservation {reservation_id}: {e}")

def send_reservation_cancellation_email(reservation_id):
    """
    Send reservation cancellation email in a thread
    """
    from .models import Reservation
    
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        user = reservation.user
        
        subject = f"❌ Reservation Cancelled - {reservation.movie_detail.movie.title}"
        
        message = (
            f"Hello {user.first_name or user.username},\n\n"
            f"Your movie reservation has been cancelled.\n\n"
            f"📋 Cancelled Reservation Details:\n"
            f"Movie: {reservation.movie_detail.movie.title}\n"
            f"Cinema: {reservation.cinema_name}\n"
            f"Date: {reservation.selected_date}\n"
            f"Showtime: {reservation.selected_showtime}\n"
            f"Number of Seats: {reservation.number_of_seats}\n"
            f"Seats: {', '.join(reservation.selected_seats) if reservation.selected_seats else 'Not specified'}\n"
            f"Reservation ID: {reservation.id}\n\n"
            f"If this was a mistake or you'd like to make a new reservation, "
            f"please visit our website.\n\n"
            f"We hope to see you at the cinema soon!"
        )
        
        print(f"🟡 Thread: Sending cancellation email to {user.email}")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        print(f"🟢 Thread: Cancellation email sent successfully for reservation {reservation_id}")
        
    except Reservation.DoesNotExist:
        print(f"🔴 Thread: Reservation {reservation_id} not found")
        logger.error(f"Reservation {reservation_id} not found for cancellation email")
    except Exception as e:
        print(f"🔴 Thread: Error sending cancellation email: {e}")
        logger.error(f"Error sending cancellation email for reservation {reservation_id}: {e}")

# Optional: Enhanced email thread with retry logic
class EmailThread(threading.Thread):
    """
    Enhanced email thread with error handling and optional retry logic
    """
    def __init__(self, email_function, reservation_id, max_retries=3):
        threading.Thread.__init__(self)
        self.email_function = email_function
        self.reservation_id = reservation_id
        self.max_retries = max_retries
        self.daemon = True
        
    def run(self):
        retries = 0
        while retries < self.max_retries:
            try:
                self.email_function(self.reservation_id)
                break  # Success, exit retry loop
            except Exception as e:
                retries += 1
                if retries < self.max_retries:
                    print(f"🟡 Retry {retries}/{self.max_retries} for reservation {self.reservation_id}")
                    import time
                    time.sleep(2 ** retries)  # Exponential backoff
                else:
                    print(f"🔴 All retries failed for reservation {self.reservation_id}: {e}")
                    logger.error(f"All email retries failed for reservation {self.reservation_id}: {e}")

# Enhanced email sending functions using the EmailThread class
def send_reservation_confirmation_email_enhanced(reservation_id):
    """Enhanced version with retry logic"""
    email_thread = EmailThread(send_reservation_confirmation_email, reservation_id)
    email_thread.start()

def send_reservation_reminder_email_enhanced(reservation_id):
    """Enhanced version with retry logic"""
    email_thread = EmailThread(send_reservation_reminder_email, reservation_id)
    email_thread.start()

def send_reservation_cancellation_email_enhanced(reservation_id):
    """Enhanced version with retry logic"""
    email_thread = EmailThread(send_reservation_cancellation_email, reservation_id)
    email_thread.start()