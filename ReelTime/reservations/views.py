# reservations/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Reservation
from .forms import ReservationEditForm

@login_required
def user_reservations_view(request):
    if request.user.is_admin:
        reservations = Reservation.objects.filter(
            movie_detail__admin=request.user
        ).select_related('user', 'movie_detail__movie').order_by('-reservation_date')
    else:
        reservations = Reservation.objects.filter(user=request.user).order_by('-reservation_date')
    
    return render(request, 'reservations/reservations.html', {'reservations': reservations})

@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check permissions
    if not request.user.is_admin and reservation.user != request.user:
        messages.error(request, "You don't have permission to edit this reservation.")
        return redirect('reservations')
    
    # Check if reservation can be modified
    if not reservation.can_be_modified():
        messages.error(request, "This reservation can no longer be modified (within 2 hours of showtime).")
        return redirect('reservations')
    
    if request.method == 'POST':
        form = ReservationEditForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, "Reservation updated successfully!")
            return redirect('reservations')
    else:
        form = ReservationEditForm(instance=reservation)
    
    return render(request, 'reservations/edit_reservation.html', {
        'form': form,
        'reservation': reservation
    })

@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check permissions
    if not request.user.is_admin and reservation.user != request.user:
        messages.error(request, "You don't have permission to cancel this reservation.")
        return redirect('reservations')
    
    # Check if reservation can be cancelled
    if not reservation.can_be_cancelled():
        messages.error(request, "This reservation can no longer be cancelled (within 1 hour of showtime).")
        return redirect('reservations')
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        
        # Send cancellation email
        reservation.send_cancellation_email()
        
        messages.success(request, "Reservation cancelled successfully!")
        return redirect('reservations')
    
    return render(request, 'reservations/cancel_reservation.html', {
        'reservation': reservation
    })

@login_required
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check permissions - only admin or reservation owner can delete
    if not request.user.is_admin and reservation.user != request.user:
        messages.error(request, "You don't have permission to delete this reservation.")
        return redirect('reservations')
    
    if request.method == 'POST':
        # For admin, allow deletion; for users, only allow if not too close to showtime
        if request.user.is_admin or reservation.can_be_cancelled():
            reservation.delete()
            messages.success(request, "Reservation deleted successfully!")
        else:
            messages.error(request, "This reservation can no longer be deleted (within 1 hour of showtime).")
        
        return redirect('reservations')
    
    return render(request, 'reservations/delete_reservation.html', {
        'reservation': reservation
    })