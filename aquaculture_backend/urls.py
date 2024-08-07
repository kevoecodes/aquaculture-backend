from django.contrib import admin
from django.urls import path
from aqua.views import LoginView, DeviceReadingsView, DevicesView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login', LoginView.as_view()),
    path('api/v1/device-info', DeviceReadingsView.as_view()),
    path('api/v1/devices', DevicesView.as_view()),
]
