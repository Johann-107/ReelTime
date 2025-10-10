import random
import string
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    username = models.CharField(max_length=50, unique=True, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(max_length=15, unique=True, blank=False, null=False)
    password = models.CharField(max_length=128, blank=False, null=False)

    # Admin-specific fields
    is_admin = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False)
    cinema_name = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        """Custom validation before saving."""
        # Regular users: no spaces allowed in username
        if not self.is_admin and ' ' in self.username:
            raise ValidationError("Username cannot contain spaces.")

    def save(self, *args, **kwargs):
        # Auto-generate username if empty
        if not self.username:
            random_id = ''.join(random.choices(string.digits, k=4))
            self.username = f"user{random_id}"

        # Run clean() before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username