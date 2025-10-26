from django.contrib import admin
from .models import Movie, MovieAdminDetails, Reservation

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'rating', 'duration_minutes')
    search_fields = ('title', 'genre', 'director')
    list_filter = ('genre', 'rating')

@admin.register(MovieAdminDetails)
class MovieAdminDetailsAdmin(admin.ModelAdmin):
    list_display = ('movie', 'admin', 'release_date', 'end_date', 'is_now_showing')
    list_filter = ('release_date', 'end_date')
    search_fields = ('movie__title', 'admin__cinema_name')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie_detail', 'cinema_name', 'showtime', 'number_of_seats', 'status', 'reservation_date')
    list_filter = ('status', 'reservation_date')
    search_fields = ('user__email', 'cinema_name', 'movie_detail__movie__title')
    readonly_fields = ('reservation_date',)
