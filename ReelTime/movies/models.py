from django.db import models
from django.utils import timezone

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    end_date = models.DateField()
    showing_times = models.JSONField(default=list, blank=True)  # e.g., ["10:00 AM", "1:30 PM", "6:45 PM"]
    poster = models.ImageField(upload_to='movies/posters/', blank=True, null=True)

    # Optional attributes
    genre = models.CharField(max_length=100, blank=True)
    director = models.CharField(max_length=255, blank=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    rating = models.CharField(max_length=10, blank=True)  # e.g., "PG-13", "R", etc.
    
    @property
    def is_now_showing(self):
        """Return True if the movie is currently showing."""
        today = timezone.now().date()
        return self.release_date <= today <= self.end_date

    @property
    def coming_soon(self):
        """Return True if the movie is not yet released."""
        today = timezone.now().date()
        return today < self.release_date
    
    def __str__(self):
        return self.title