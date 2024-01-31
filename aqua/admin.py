from django.contrib import admin
from aqua.models import Device, Reading, UserDevice

# Register your models here.
admin.site.register(Device)
admin.site.register(Reading)
admin.site.register(UserDevice)
