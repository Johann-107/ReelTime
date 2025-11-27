from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import date, timedelta
from halls.models import Hall
from cloudinary.models import CloudinaryField

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

    poster = CloudinaryField(
        'poster', 
        folder='movies/posters/', 
        blank=True, 
        null=True,
        transformation={
            'quality': 'auto:low',
            'width': 400,
            'height': 600,
            'crop': 'fill'
        }
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('movie', 'admin', 'release_date', 'end_date')

    @property
    def is_now_showing(self):
        """Return True if the movie is currently showing."""
        today = timezone.now().date()
        return self.release_date <= today <= self.end_date

    @property
    def poster_url(self):
        """Return the Cloudinary URL for the poster with transformations."""
        if self.poster:
            # Check if it's a Cloudinary resource or an uploaded file
            if hasattr(self.poster, 'build_url'):
                return self.poster.build_url(
                    width=400,
                    height=600,
                    crop="fill",
                    quality="auto",
                    format="webp"
                )
            else:
                # It's an uploaded file during form processing
                # Return the URL directly or handle appropriately
                try:
                    # For form preview, you might need to handle this differently
                    return str(self.poster)
                except:
                    return None
        return None

    @property
    def poster_thumbnail_url(self):
        """Return a thumbnail version of the poster."""
        if self.poster:
            if hasattr(self.poster, 'build_url'):
                return self.poster.build_url(
                    width=200,
                    height=300,
                    crop="fill",
                    quality="auto",
                    format="webp"
                )
            else:
                try:
                    return str(self.poster)
                except:
                    return None
        return None
    
    def get_remaining_seats(self, showtime):
        """Return the remaining number of seats for the given showtime."""
        from reservations.models import Reservation

        showtime_info = next((s for s in self.showing_times if s["time"] == showtime), None)
        if not showtime_info:
            return 0

        total = showtime_info.get("max_seats", 0)

        reserved = Reservation.objects.filter(
            movie_detail=self,
            selected_showtime=showtime
        ).aggregate(total_reserved=models.Sum('number_of_seats'))['total_reserved'] or 0

        return total - reserved

    def __str__(self):
        return f"{self.admin.username}'s details for {self.movie.title}"