# reservations/utils.py
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

def send_reservation_confirmation_email(reservation_id):
    """
    Send reservation confirmation email using SendGrid
    """
    from .models import Reservation
    
    try:
        print(f"🟡 SendGrid: Sending confirmation email for reservation {reservation_id}")
        reservation = Reservation.objects.get(id=reservation_id)
        user = reservation.user
        
        subject = f"🎬 Reservation Confirmed - {reservation.movie_detail.movie.title}"
        
        # Plain text content
        plain_text_message = (
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
        
        # HTML content (optional but recommended)
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎬 Reservation Confirmed!</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{user.first_name or user.username}</strong>,</p>
                <p>Your movie reservation has been confirmed!</p>
                
                <div class="details">
                    <h3>📋 Reservation Details:</h3>
                    <p><strong>Movie:</strong> {reservation.movie_detail.movie.title}</p>
                    <p><strong>Cinema:</strong> {reservation.cinema_name}</p>
                    <p><strong>Date:</strong> {reservation.selected_date}</p>
                    <p><strong>Showtime:</strong> {reservation.selected_showtime}</p>
                    <p><strong>Number of Seats:</strong> {reservation.number_of_seats}</p>
                    <p><strong>Seats:</strong> {', '.join(reservation.selected_seats) if reservation.selected_seats else 'Not specified'}</p>
                    <p><strong>Total Cost:</strong> ${reservation.total_cost}</p>
                    <p><strong>Reservation ID:</strong> {reservation.id}</p>
                </div>
                
                <p>We look forward to seeing you at the cinema!</p>
            </div>
            <div class="footer">
                <p>Thank you for choosing <strong>ReelTime</strong>!</p>
            </div>
        </body>
        </html>
        """
        
        # Send email using SendGrid
        success = send_sendgrid_email(
            to_email=user.email,
            subject=subject,
            plain_text_content=plain_text_message,
            html_content=html_message
        )
        
        if success:
            print(f"🟢 SendGrid: Confirmation email sent successfully for reservation {reservation_id}")
        else:
            print(f"🔴 SendGrid: Failed to send confirmation email for reservation {reservation_id}")
            
        return success
        
    except Reservation.DoesNotExist:
        print(f"🔴 SendGrid: Reservation {reservation_id} not found")
        logger.error(f"Reservation {reservation_id} not found for confirmation email")
        return False
    except Exception as e:
        print(f"🔴 SendGrid: Error sending confirmation email: {e}")
        logger.error(f"Error sending confirmation email for reservation {reservation_id}: {e}")
        return False

def send_reservation_reminder_email(reservation_id):
    """
    Send reservation reminder email using SendGrid
    """
    from .models import Reservation
    
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        user = reservation.user
        
        subject = f"⏰ Movie Reminder - {reservation.movie_detail.movie.title} tomorrow!"
        
        # Plain text content
        plain_text_message = (
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
        
        # HTML content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #fff3cd; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⏰ Movie Reminder!</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{user.first_name or user.username}</strong>,</p>
                <p>This is a friendly reminder about your movie reservation <strong>tomorrow</strong>!</p>
                
                <div class="details">
                    <h3>🎟️ Your Reservation:</h3>
                    <p><strong>Movie:</strong> {reservation.movie_detail.movie.title}</p>
                    <p><strong>Cinema:</strong> {reservation.cinema_name}</p>
                    <p><strong>Date:</strong> {reservation.selected_date}</p>
                    <p><strong>Showtime:</strong> {reservation.selected_showtime}</p>
                    <p><strong>Seats:</strong> {', '.join(reservation.selected_seats) if reservation.selected_seats else 'Not specified'}</p>
                </div>
                
                <p><strong>Please arrive at least 15 minutes before the showtime.</strong></p>
                <p>Enjoy your movie experience! 🍿</p>
            </div>
        </body>
        </html>
        """
        
        success = send_sendgrid_email(
            to_email=user.email,
            subject=subject,
            plain_text_content=plain_text_message,
            html_content=html_message
        )
        
        return success
        
    except Exception as e:
        print(f"🔴 SendGrid: Error sending reminder email: {e}")
        logger.error(f"Error sending reminder email for reservation {reservation_id}: {e}")
        return False

def send_reservation_cancellation_email(reservation_id):
    """
    Send reservation cancellation email using SendGrid
    """
    from .models import Reservation
    
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        user = reservation.user
        
        subject = f"❌ Reservation Cancelled - {reservation.movie_detail.movie.title}"
        
        # Plain text content
        plain_text_message = (
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
        
        # HTML content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8d7da; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>❌ Reservation Cancelled</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{user.first_name or user.username}</strong>,</p>
                <p>Your movie reservation has been cancelled.</p>
                
                <div class="details">
                    <h3>📋 Cancelled Reservation Details:</h3>
                    <p><strong>Movie:</strong> {reservation.movie_detail.movie.title}</p>
                    <p><strong>Cinema:</strong> {reservation.cinema_name}</p>
                    <p><strong>Date:</strong> {reservation.selected_date}</p>
                    <p><strong>Showtime:</strong> {reservation.selected_showtime}</p>
                    <p><strong>Number of Seats:</strong> {reservation.number_of_seats}</p>
                    <p><strong>Seats:</strong> {', '.join(reservation.selected_seats) if reservation.selected_seats else 'Not specified'}</p>
                    <p><strong>Reservation ID:</strong> {reservation.id}</p>
                </div>
                
                <p>If this was a mistake or you'd like to make a new reservation, please visit our website.</p>
                <p>We hope to see you at the cinema soon!</p>
            </div>
        </body>
        </html>
        """
        
        success = send_sendgrid_email(
            to_email=user.email,
            subject=subject,
            plain_text_content=plain_text_message,
            html_content=html_message
        )
        
        return success
        
    except Reservation.DoesNotExist:
        print(f"🔴 SendGrid: Reservation {reservation_id} not found")
        logger.error(f"Reservation {reservation_id} not found for cancellation email")
        return False
    except Exception as e:
        print(f"🔴 SendGrid: Error sending cancellation email: {e}")
        logger.error(f"Error sending cancellation email for reservation {reservation_id}: {e}")
        return False