import random
import string
from django.db import models

# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    username = models.CharField(max_length=50, unique=True, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(max_length=15, unique=True, blank=False, null=False)
    password = models.CharField(max_length=128, blank=False, null=False)
    
    def save(self, *args, **kwargs):
        # 👇 if username is empty, generate one automatically
        if not self.username:
            random_id = ''.join(random.choices(string.digits, k=4))
            self.username = f"user{random_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
