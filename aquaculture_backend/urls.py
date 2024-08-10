from django.contrib import admin
from django.urls import path
from aqua.views import LoginView, DeviceReadingsView, DevicesView, GetUserFromTokenView, SwitchView, ListDevicesView, \
    DeviceDetailsView, ListDevicesReadingsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login', LoginView.as_view()),
    path('api/v1/device-info', DeviceReadingsView.as_view()),
    path('api/v1/devices', DevicesView.as_view()),
    path('api/v1/auth/user-from-token', GetUserFromTokenView.as_view()),
    path('api/v1/switch-motor', SwitchView.as_view()),

    path('api/v1/list-devices', ListDevicesView.as_view()),
    path('api/v1/list-readings', ListDevicesReadingsView.as_view()),
    path('api/v1/device/<str:pk>', DeviceDetailsView.as_view()),
]
