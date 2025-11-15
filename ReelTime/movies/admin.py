from django.contrib import admin
from .models import Movie, MovieAdminDetails

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