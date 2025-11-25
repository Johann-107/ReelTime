from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import date, timedelta
from halls.models import Hall


def get_tomorrow():
    return date.today() + timedelta(days=1)


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Optional attributes
    genre = models.CharField(max_length=100, blank=True)
    director = models.CharField(max_length=255, blank=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    rating = models.CharField(max_length=10, blank=True)  # e.g., "PG-13", "R", etc.
    
    def __str__(self):
        return self.title
    

class MovieAdminDetails(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='admin_details')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, null=True)
    
    # Admin-specific fields
    release_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Added price field

    showing_times = models.JSONField(default=list, blank=True)

    poster = models.ImageField(upload_to='movies/posters/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('movie', 'admin', 'release_date', 'end_date')  # Prevent same admin adding same movie twice


    @property
    def is_now_showing(self):
        """Return True if the movie is currently showing."""
        today = timezone.now().date()
        return self.release_date <= today <= self.end_date

    
    def get_remaining_seats(self, showtime):
        """Return the remaining number of seats for the given showtime."""
        from reservations.models import Reservation  # local import to avoid circular dependency

        showtime_info = next((s for s in self.showing_times if s["time"] == showtime), None)
        if not showtime_info:
            return 0

        total = showtime_info.get("max_seats", 0)

        reserved = Reservation.objects.filter(
            movie_detail=self,          # correct field name
            selected_showtime=showtime  # correct field name
        ).aggregate(total_reserved=models.Sum('number_of_seats'))['total_reserved'] or 0

        return total - reserved

    def __str__(self):
        return f"{self.admin.username}'s details for {self.movie.title}"