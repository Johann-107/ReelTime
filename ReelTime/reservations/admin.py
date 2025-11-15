from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'movie_detail',
        'cinema_name',
        'selected_date',
        'selected_showtime',
        'number_of_seats',
        'status',
        'reservation_date',
    )
    list_filter = ('status', 'selected_date', 'cinema_name')
    search_fields = ('user__email', 'movie_detail__movie__title', 'cinema_name')