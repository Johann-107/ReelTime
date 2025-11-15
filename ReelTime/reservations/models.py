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
    
    # 🆕 Store the selected seat IDs as a JSON list
    selected_seats = models.JSONField(default=list, blank=True)

    reservation_date = models.DateTimeField(auto_now_add=True)

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
        # Only adjust seats on new reservation
        if not self.pk:
            # Remaining seats for this showtime
            remaining = self.movie_detail.get_remaining_seats(self.selected_showtime)

            # Ensure selected_seats is a list
            if isinstance(self.selected_seats, str):
                self.selected_seats = json.loads(self.selected_seats)

            # Validate seat count
            if len(self.selected_seats) != self.number_of_seats:
                raise ValueError(f"Number of selected seats ({len(self.selected_seats)}) "
                                 f"does not match number_of_seats ({self.number_of_seats}).")

            if len(self.selected_seats) > remaining:
                raise ValueError("Not enough seats available for this showing.")

        super().save(*args, **kwargs)
