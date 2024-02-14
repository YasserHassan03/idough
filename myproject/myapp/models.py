from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)

class RaspberryPi(models.Model):
    id = models.TextField(max_length=50, primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    # microservice_port = models.IntegerField(null=True, blank=True)
    start = models.BooleanField(default=False)

    def __str__(self):
        return self.id

