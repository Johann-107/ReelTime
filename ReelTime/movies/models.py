from django.db import models
from django.utils import timezone
from django.conf import settings

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
    
    # Admin-specific fields
    release_date = models.DateField()
    end_date = models.DateField()
    showing_times = models.JSONField(default=list, blank=True)  # e.g., ["10:00 AM", "1:30 PM", "6:45 PM"]
    poster = models.ImageField(upload_to='movies/posters/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('movie', 'admin', 'release_date', 'end_date')  # Prevent same admin adding same showtime twice

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
        return f"{self.admin.username}'s details for {self.movie.title}"