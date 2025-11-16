# reservations/models.py
from django.db import models
from django.conf import settings
from movies.models import MovieAdminDetails
from datetime import date, timedelta
import json

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
    
    # Add email tracking fields
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
        return f"{self.user.email} - {self.movie_detail.movie.title} ({self.selected_date} {self.selected_showtime})"

    def save(self, *args, **kwargs):
        is_new = not self.pk
        print(f"🟡 save() called - is_new: {is_new}, status: {self.status}")
        
        # ... your existing save logic ...
        super().save(*args, **kwargs)
        
        # Send confirmation email for new confirmed reservations
        if is_new and self.status == 'confirmed' and not self.confirmation_sent:
            print(f"🟡 Conditions met! Calling send_confirmation_email()")
            self.send_confirmation_email()
        else:
            print(f"🔴 Conditions NOT met: is_new={is_new}, status={self.status}, confirmation_sent={self.confirmation_sent}")


    def send_confirmation_email(self):
        """Send reservation confirmation email"""
        try:
            print(f"🟡 send_confirmation_email() called for user: {self.user.email}")
            from reservations.utils import send_reservation_confirmation_email
            send_reservation_confirmation_email(self)
            self.confirmation_sent = True
            Reservation.objects.filter(pk=self.pk).update(confirmation_sent=True)
            print("🟢 Confirmation email sent successfully!")
            return True
        except Exception as e:
            print(f"🔴 Failed to send confirmation email: {e}")
            return False
        

    def send_reminder_email(self):
        """Send reservation reminder email"""
        try:
            from reservations.utils import send_reservation_reminder_email  # ✅ Fix import
            send_reservation_reminder_email(self)
            self.reminder_sent = True
            Reservation.objects.filter(pk=self.pk).update(reminder_sent=True)
            return True
        except Exception as e:
            print(f"Failed to send reminder email: {e}")
            return False