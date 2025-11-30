from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from movies.models import MovieAdminDetails
from datetime import date, timedelta, datetime
import threading
from .utils import send_reservation_confirmation_email, send_reservation_cancellation_email, send_reservation_reminder_email

def get_tomorrow():
    return date.today() + timedelta(days=1)

class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    movie_detail = models.ForeignKey(MovieAdminDetails, on_delete=models.CASCADE, related_name='reservations')
    cinema_name = models.CharField(max_length=255)
    selected_date = models.DateField(default=get_tomorrow)
    selected_showtime = models.CharField(max_length=50)
    number_of_seats = models.PositiveIntegerField(default=1)
    selected_seats = models.JSONField(default=list, blank=True)
    reservation_date = models.DateTimeField(auto_now_add=True)
    
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    confirmation_sent = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-reservation_date']
        db_table = 'movies_reservation'

    def __str__(self):
        return f"{self.user.email} - {self.movie_detail.movie.title} ({self.selected_date} {self.selected_showtime}) - ${self.total_cost}"

    def clean(self):
        """Validate reservation data"""
        # Convert selected_date to date object if it's a string
        reservation_date = self.selected_date
        if isinstance(reservation_date, str):
            # Parse string date in YYYY-MM-DD format
            reservation_date = datetime.strptime(reservation_date, '%Y-%m-%d').date()
        
        if reservation_date < date.today():
            raise ValidationError("Cannot make reservations for past dates.")
        
        # Validate against movie end date
        if self.movie_detail and self.movie_detail.end_date:
            if reservation_date > self.movie_detail.end_date:
                raise ValidationError(
                    f"Cannot make reservations beyond the movie's end date ({self.movie_detail.end_date}). "
                    f"This movie is only showing until {self.movie_detail.end_date}."
                )
        
        if self.number_of_seats < 1:
            raise ValidationError("Number of seats must be at least 1.")
        
        if self.number_of_seats > 10:  # Reasonable limit
            raise ValidationError("Cannot reserve more than 10 seats at once.")

    def calculate_total_cost(self):
        """Calculate total cost based on price per seat and number of seats"""
        return self.movie_detail.price * self.number_of_seats

    def can_be_modified(self):
        """Check if reservation can be modified (not within 2 hours of showtime)"""
        if self.status == 'cancelled':
            return False
            
        # Parse showtime and date to check if it's within 2 hours
        try:
            showtime_dt = datetime.combine(self.selected_date, datetime.strptime(self.selected_showtime, '%I:%M %p').time())
            now = datetime.now()
            time_diff = showtime_dt - now
            return time_diff.total_seconds() > 7200  # 2 hours in seconds
        except:
            return True

    def can_be_cancelled(self):
        """Check if reservation can be cancelled (not within 1 hour of showtime)"""
        if self.status == 'cancelled':
            return False
            
        try:
            showtime_dt = datetime.combine(self.selected_date, datetime.strptime(self.selected_showtime, '%I:%M %p').time())
            now = datetime.now()
            time_diff = showtime_dt - now
            return time_diff.total_seconds() > 3600  # 1 hour in seconds
        except:
            return True
    
    def is_same_day_showing(self):
        """Check if the showing date is today"""
        from datetime import date
        return self.selected_date == date.today()

    def save(self, *args, **kwargs):
        is_new = not self.pk
        
        # Calculate total cost before saving
        if self.movie_detail and self.movie_detail.price is not None:
            self.total_cost = self.calculate_total_cost()
        else:
            self.total_cost = 0.00
            
        # Validate before saving
        self.clean()
            
        super().save(*args, **kwargs)
        
        # Send confirmation email for new confirmed reservations using threading
        if is_new and self.status == 'confirmed' and not self.confirmation_sent:
            self.send_confirmation_email()

    def send_confirmation_email(self):
        """Send reservation confirmation email using threading"""
        try:
            # Start email sending in a separate thread
            email_thread = threading.Thread(
                target=send_reservation_confirmation_email,
                args=(self.id,)
            )
            email_thread.daemon = True  # Thread will close when main program exits
            email_thread.start()
            print(f"🟡 Confirmation email thread started for reservation {self.id}")
            return True
        except Exception as e:
            print(f"🔴 Failed to start confirmation email thread: {e}")
            return False

    def send_cancellation_email(self):
        """Send reservation cancellation email using threading"""
        try:
            # Start email sending in a separate thread
            email_thread = threading.Thread(
                target=send_reservation_cancellation_email,
                args=(self.id,)
            )
            email_thread.daemon = True
            email_thread.start()
            print(f"🟡 Cancellation email thread started for reservation {self.id}")
            return True
        except Exception as e:
            print(f"🔴 Failed to start cancellation email thread: {e}")
            return False
        
    def send_reminder_email(self):
        """Send reservation reminder email using threading"""
        try:
            # Start email sending in a separate thread
            email_thread = threading.Thread(
                target=send_reservation_reminder_email,
                args=(self.id,)
            )
            email_thread.daemon = True
            email_thread.start()
            print(f"🟡 Reminder email thread started for reservation {self.id}")
            return True
        except Exception as e:
            print(f"🔴 Failed to start reminder email thread: {e}")
            return False