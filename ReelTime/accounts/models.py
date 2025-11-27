import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False)
    cinema_name = models.CharField(max_length=100, blank=True, null=True)

    profile_picture = CloudinaryField(
        'profile_picture',
        folder='users/profile_pictures/',
        blank=True,
        null=True,
        transformation={
            'width': 200,
            'height': 200,
            'crop': 'fill',
            'gravity': 'face',
            'quality': 'auto'
        }
    )

    def clean(self):
        if not self.is_admin and ' ' in self.username:
            raise ValidationError("Username cannot contain spaces.")

    def save(self, *args, **kwargs):
        if not self.username:
            random_id = ''.join(random.choices(string.digits, k=4))
            self.username = f"user{random_id}"
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def profile_picture_url(self):
        """Safe method to get profile picture URL with transformations"""
        if self.profile_picture:
            try:
                if hasattr(self.profile_picture, 'build_url'):
                    return self.profile_picture.build_url(
                        width=200,
                        height=200,
                        crop="fill",
                        gravity="face",
                        quality="auto",
                        format="webp"
                    )
                elif hasattr(self.profile_picture, 'url'):
                    return self.profile_picture.url
            except (AttributeError, Exception):
                pass
        return None
    
    @property
    def profile_picture_thumbnail_url(self):
        """Get thumbnail version for smaller displays"""
        if self.profile_picture:
            try:
                if hasattr(self.profile_picture, 'build_url'):
                    return self.profile_picture.build_url(
                        width=50,
                        height=50,
                        crop="fill",
                        gravity="face",
                        quality="auto",
                        format="webp"
                    )
                elif hasattr(self.profile_picture, 'url'):
                    return self.profile_picture.url
            except (AttributeError, Exception):
                pass
        return None
    
    def delete_profile_picture(self):
        """Delete profile picture from Cloudinary"""
        if self.profile_picture:
            self.profile_picture.delete()
            self.profile_picture = None
            self.save()

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'reel_time_user'


class PendingAdmin(models.Model):
    cinema_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=100, unique=True)
    is_confirmed = models.BooleanField(default=False)  # ✅ Added this field
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        status = "Confirmed" if self.is_confirmed else "Pending"
        return f"{self.cinema_name} - {self.email} ({status})"

    class Meta:
        ordering = ["-created_at"]  # optional: latest requests first