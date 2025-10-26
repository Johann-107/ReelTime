from django.apps import AppConfig
import os

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """
        Run once when Django starts to ensure no sessions are active.
        Only runs once during initial startup, not on auto-reload.
        """
        # Only run when Django is in the main process (skip on initial load)
        if os.environ.get('RUN_MAIN') == 'true':
            # Skip if explicitly disabled
            if os.environ.get('DJANGO_CLEAR_SESSIONS') == 'false':
                return
                
            try:
                # Import here to avoid "Apps aren't loaded yet" error
                from django.contrib.sessions.models import Session  
                Session.objects.all().delete()
                print("✅ All user sessions cleared on startup.")
            except Exception as e:
                print(f"⚠️ Could not clear sessions on startup: {e}")
