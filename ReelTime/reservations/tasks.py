# reservations/tasks.py
from background_task import background
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

@background(schedule=5)  # Schedule to run 5 seconds from now
def send_reservation_confirmation_email_task(reservation_id):
    """
    Background task to send reservation confirmation email
    """
    from .models import Reservation
    
    try:
        print(f"🟡 Background task: Sending confirmation email for reservation {reservation_id}")
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
            f"Seats: {', '.join(reservation.selected_seats)}\n"
            f"Reservation ID: {reservation.id}\n\n"
            f"We look forward to seeing you at the cinema!\n\n"
            f"Thank you for choosing ReelTime!"
        )
        
        print(f"🟡 Background task: Sending email to {user.email}")
        
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
        
        print(f"🟢 Background task: Confirmation email sent successfully for reservation {reservation_id}")
        
    except Reservation.DoesNotExist:
        print(f"🔴 Background task: Reservation {reservation_id} not found")
    except Exception as e:
        print(f"🔴 Background task: Error sending confirmation email: {e}")
        # The task will be retried based on MAX_ATTEMPTS

@background(schedule=5)
def send_reservation_reminder_email_task(reservation_id):
    """
    Background task to send reservation reminder email
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
            f"Seats: {', '.join(reservation.selected_seats)}\n\n"
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
        
        print(f"🟢 Background task: Reminder email sent successfully for reservation {reservation_id}")
        
    except Exception as e:
        print(f"🔴 Background task: Error sending reminder email: {e}")

@background(schedule=5)
def send_reservation_cancellation_email_task(reservation_id):
    """
    Background task to send reservation cancellation email
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
            f"Seats: {', '.join(reservation.selected_seats)}\n"
            f"Reservation ID: {reservation.id}\n\n"
            f"If this was a mistake or you'd like to make a new reservation, "
            f"please visit our website.\n\n"
            f"We hope to see you at the cinema soon!"
        )
        
        print(f"🟡 Background task: Sending cancellation email to {user.email}")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        print(f"🟢 Background task: Cancellation email sent successfully for reservation {reservation_id}")
        
    except Reservation.DoesNotExist:
        print(f"🔴 Background task: Reservation {reservation_id} not found")
    except Exception as e:
        print(f"🔴 Background task: Error sending cancellation email: {e}")