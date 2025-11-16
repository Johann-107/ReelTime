# reservations/management/commands/send_reservation_reminders.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reservations.models import Reservation

class Command(BaseCommand):
    help = 'Send reminder emails for reservations happening tomorrow'

    def handle(self, *args, **options):
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # Get confirmed reservations for tomorrow that haven't had reminders sent
        reservations = Reservation.objects.filter(
            selected_date=tomorrow,
            status='confirmed',
            reminder_sent=False
        ).select_related('user', 'movie_detail__movie')
        
        self.stdout.write(f"Found {reservations.count()} reservations for tomorrow")
        
        success_count = 0
        for reservation in reservations:
            try:
                if reservation.send_reminder_email():
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Sent reminder for reservation {reservation.id} to {reservation.user.email}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to send reminder for reservation {reservation.id}"
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error sending reminder for reservation {reservation.id}: {str(e)}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully sent {success_count} reminder emails"
            )
        )