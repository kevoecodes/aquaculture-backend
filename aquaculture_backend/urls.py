from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path
from aqua.views import LoginApiView, DeviceReadingsView, DevicesView, GetUserFromTokenView, SwitchView, ListDevicesView, \
    DeviceDetailsView, ListDevicesReadingsView, login_request, DashboardView, ReadingsView, logout_user, \
    export_excel_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login', LoginApiView.as_view()),
    path('api/v1/device-info', DeviceReadingsView.as_view()),
    path('api/v1/devices', DevicesView.as_view()),
    path('api/v1/auth/user-from-token', GetUserFromTokenView.as_view()),
    path('api/v1/switch-motor', SwitchView.as_view()),

    path('api/v1/list-devices', ListDevicesView.as_view()),
    path('api/v1/list-readings', ListDevicesReadingsView.as_view()),
    path('api/v1/device/<str:pk>', DeviceDetailsView.as_view()),

    path('login/', LoginView.as_view(template_name="login.html", next_page="home"), name="login"),
    path('', DashboardView.as_view(), name="dashboard-view"),
    path('login/login-page', login_request, name='login-request'),
    path('readings', ReadingsView.as_view(), name='readings'),
    path('logout', logout_user, name='logout'),
    path('export-excel', export_excel_data, name='export-excel'),
]
