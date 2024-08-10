from django.contrib.auth.models import User
from django.db import models


class Device(models.Model):

    device_no = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Reading(models.Model):

    temperature = models.FloatField(default=0.0)
    ph = models.FloatField(default=0.0)
    turbidity = models.FloatField(default=0.0)
    ammonia = models.FloatField(default=0.0)
    dissolved_oxygen = models.FloatField(default=0.0)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

