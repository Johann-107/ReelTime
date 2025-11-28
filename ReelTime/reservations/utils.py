# reservations/utils.py

# You can keep these functions for direct usage, but they'll now be called via background tasks
def send_reservation_confirmation_email(reservation):
    """Legacy function - now handled by background tasks"""
    print("🟡 Using background task for email sending")
    return reservation.send_confirmation_email()

def send_reservation_reminder_email(reservation):
    """Legacy function - now handled by background tasks"""
    print("🟡 Using background task for reminder email")
    return reservation.send_reminder_email()

def send_reservation_cancellation_email(reservation):
    """Legacy function - now handled by background tasks"""
    print("🟡 Using background task for cancellation email")
    return reservation.send_cancellation_email()