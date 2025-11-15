from django.db import models
from django.conf import settings


# Create your models here.
class Hall(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_admin': True},
        related_name='halls'
    )
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    
    layout = models.JSONField(default=dict, blank=True)  # stores grid & objects position

    def __str__(self):
        return f"{self.name} ({self.admin.cinema_name})"
