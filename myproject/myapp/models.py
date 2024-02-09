from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add custom fields if needed
    bio = models.TextField(max_length=500, blank=True)
