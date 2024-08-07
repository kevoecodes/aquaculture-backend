from django.contrib.auth.models import User
from django.db import models


class Device(models.Model):

    device_no = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Reading(models.Model):

    temperature = models.FloatField()
    ph = models.FloatField()
    turbidity = models.FloatField()
    ammonia = models.FloatField()
    dissolved_oxygen = models.FloatField()
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)


class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

