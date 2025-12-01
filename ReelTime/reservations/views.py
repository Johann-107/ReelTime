# re# reservations/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, date
from .models import Reservation
from .forms import ReservationEditForm
import json

@login_required
def user_reservations_view(request):
    today = timezone.now().date()
    
    if request.user.is_admin:
        # Get only future reservations for admin view
        reservations = Reservation.objects.filter(
            movie_detail__admin=request.user,
            selected_date__gte=today
        ).select_related('user', 'movie_detail__movie', 'movie_detail__hall')
    else:
        # Get only future reservations for regular users
        reservations = Reservation.objects.filter(
            user=request.user,
            selected_date__gte=today
        ).select_related('movie_detail__movie', 'movie_detail__hall')
    
    # Sort reservations: confirmed first, then by selected_date ascending, then by selected_showtime
    # We'll sort in Python to handle complex ordering
    reservations_list = list(reservations)
    
    # Define a key function for sorting
    def reservation_sort_key(res):
        # Primary sort: status (confirmed comes first)
        status_order = {'confirmed': 0, 'pending': 1, 'cancelled': 2}
        
        # Convert selected_showtime to comparable format if it's a time
        showtime_str = str(res.selected_showtime)
        # Handle different time formats
        try:
            # Try to parse as time
            from datetime import datetime as dt
            showtime = dt.strptime(showtime_str, '%H:%M:%S').time()
        except:
            try:
                showtime = dt.strptime(showtime_str, '%H:%M').time()
            except:
                # If parsing fails, use string comparison
                showtime = showtime_str
        
        return (
            status_order.get(res.status, 99),  # Sort by status order
            res.selected_date,                  # Then by date ascending
            showtime                           # Then by showtime
        )
    
    # Sort the reservations
    reservations_list.sort(key=reservation_sort_key)
    
    # Process each reservation to add formatted seat labels
    for reservation in reservations_list:
        if reservation.selected_seats and reservation.movie_detail.hall:
            formatted_seats = []
            
            # Get hall layout to determine seat numbering
            hall = reservation.movie_detail.hall
            if hall and hall.layout:
                try:
                    # Parse layout
                    if isinstance(hall.layout, str):
                        layout_data = json.loads(hall.layout)
                        if isinstance(layout_data, dict):
                            seat_map = layout_data.get('seat_map', [])
                        elif isinstance(layout_data, list):
                            seat_map = layout_data
                        else:
                            seat_map = []
                    elif isinstance(hall.layout, dict):
                        seat_map = hall.layout.get('seat_map', [])
                    elif isinstance(hall.layout, list):
                        seat_map = hall.layout
                    else:
                        seat_map = []
                    
                    if seat_map:
                        # Find min row for seats
                        seat_rows = [s['row'] for s in seat_map if s.get('type') == 'seat']
                        min_seat_row = min(seat_rows) if seat_rows else 0
                        
                        # Group seats by row to calculate right-to-left numbering
                        rows_dict = {}
                        for seat in seat_map:
                            if seat.get('type') == 'seat':
                                row = seat['row']
                                if row not in rows_dict:
                                    rows_dict[row] = []
                                rows_dict[row].append(seat['col'])
                        
                        # Sort columns right to left for each row
                        for row in rows_dict:
                            rows_dict[row].sort(reverse=True)
                        
                        # Convert selected seats
                        for seat_id in reservation.selected_seats:
                            try:
                                row, col = map(int, seat_id.split('-'))
                                # Calculate row letter (A, B, C, etc.)
                                row_letter = chr(65 + (row - min_seat_row))
                                # Calculate seat number (right to left)
                                if row in rows_dict and col in rows_dict[row]:
                                    seat_number = rows_dict[row].index(col) + 1
                                    formatted_seats.append(f"{row_letter}{seat_number}")
                            except:
                                pass
                except:
                    pass
            
            # Store formatted seats as a new attribute
            reservation.formatted_seat_labels = ', '.join(formatted_seats) if formatted_seats else ''
        else:
            reservation.formatted_seat_labels = ''
    
    return render(request, 'reservations/reservations.html', {'reservations': reservations_list})

@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check permissions
    if not request.user.is_admin and reservation.user != request.user:
        messages.error(request, "You don't have permission to edit this reservation.")
        return redirect('reservations')
    
    # Check if reservation is cancelled
    if reservation.status == 'cancelled':
        messages.error(request, "Cannot edit a cancelled reservation.")
        return redirect('reservations')
    
    # Check if booking is same day and user is not admin
    if reservation.is_same_day_showing() and not request.user.is_admin:
        messages.error(request, "Bookings within the day can only be edited by administrators. Please contact admin for seat selection changes.")
        return redirect('reservations')
    
    if request.method == 'POST':
        # Get the selected seats from the form
        selected_seats_json = request.POST.get('selected_seats', '[]')
        print(f"DEBUG: Received selected_seats: {selected_seats_json}")  # Debug line
        
        try:
            selected_seats = json.loads(selected_seats_json)
            print(f"DEBUG: Parsed seats: {selected_seats}, Count: {len(selected_seats)}")  # Debug line
            
            # Validate that seats were actually selected
            if not selected_seats or len(selected_seats) == 0:
                messages.error(request, "Please select at least one seat.")
            elif len(selected_seats) > reservation.number_of_seats:
                # Check if trying to select more seats than originally reserved
                messages.error(request, f"You cannot select more seats than originally reserved ({reservation.number_of_seats} seat(s)). Please select {reservation.number_of_seats} or fewer seats.")
            else:
                # Verify that selected seats are not already reserved by others
                reserved_reservations = Reservation.objects.filter(
                    movie_detail=reservation.movie_detail,
                    selected_date=reservation.selected_date,
                    selected_showtime=reservation.selected_showtime,
                    status__in=['pending', 'confirmed']
                ).exclude(id=reservation.id)
                
                reserved_seats = []
                for res in reserved_reservations:
                    if res.selected_seats:
                        reserved_seats.extend(res.selected_seats)
                
                # Check if any selected seat is already reserved
                conflicting_seats = set(selected_seats) & set(reserved_seats)
                if conflicting_seats:
                    messages.error(request, "Some of the selected seats are already reserved by other users. Please select different seats.")
                else:
                    # All validations passed, update the reservation
                    reservation.selected_seats = selected_seats
                    reservation.number_of_seats = len(selected_seats)
                    reservation.total_cost = reservation.calculate_total_cost()
                    reservation.save()
                    
                    print(f"DEBUG: Reservation saved successfully!")  # Debug line
                    messages.success(request, "Reservation updated successfully!")
                    return redirect('reservations')
                    
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")  # Debug line
            messages.error(request, "Invalid seat selection data.")
        except Exception as e:
            print(f"DEBUG: Unexpected error: {e}")  # Debug line
            messages.error(request, f"An error occurred: {str(e)}")
    
    # If we get here, either GET request or POST with validation errors
    form = ReservationEditForm(instance=reservation)
    
    # Get the hall layout for seat selection
    hall = reservation.movie_detail.hall
    if hall and hall.layout:
        # Parse layout if it's a string
        if isinstance(hall.layout, str):
            try:
                layout_data = json.loads(hall.layout)
                # Check if layout_data is a dict with 'seat_map' key, or if it's directly the seat_map list
                if isinstance(layout_data, dict):
                    seat_map = layout_data.get('seat_map', [])
                elif isinstance(layout_data, list):
                    seat_map = layout_data
                else:
                    seat_map = []
            except json.JSONDecodeError:
                seat_map = []
        elif isinstance(hall.layout, dict):
            seat_map = hall.layout.get('seat_map', [])
        elif isinstance(hall.layout, list):
            seat_map = hall.layout
        else:
            seat_map = []
    else:
        seat_map = []
    
    # Get all reservations for this showtime to mark seats as reserved
    reserved_reservations = Reservation.objects.filter(
        movie_detail=reservation.movie_detail,
        selected_date=reservation.selected_date,
        selected_showtime=reservation.selected_showtime,
        status__in=['pending', 'confirmed']
    ).exclude(id=reservation.id)  # Exclude current reservation
    
    # Collect all reserved seats
    reserved_seats = []
    for res in reserved_reservations:
        if res.selected_seats:
            reserved_seats.extend(res.selected_seats)
    
    return render(request, 'reservations/edit_reservation.html', {
        'form': form,
        'reservation': reservation,
        'seat_map': json.dumps(seat_map),
        'reserved_seats': json.dumps(reserved_seats),
        'current_selected_seats': json.dumps(reservation.selected_seats or [])
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
    
    # Only admins can delete reservations
    if not request.user.is_admin:
        messages.error(request, "Only administrators can delete reservations.")
        return redirect('reservations')
    
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, "Reservation deleted successfully!")
        return redirect('reservations')
    
    return render(request, 'reservations/delete_reservation.html', {
        'reservation': reservation
    })