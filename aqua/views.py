from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from rest_framework import status, generics, filters
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from aqua.models import Reading, Device, UserDevice
from aqua.serializers import LoginSerializer, UserSerializer, ReadingSerializer, ReadingPostSerializer, \
    UserDeviceSerializer
from aqua.sms import send_sms
from aqua.socket.managers import PostToReadingChannel


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 200
    page_size_query_param = 'page_size'
    max_page_size = 1000


class LoginApiView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        print(request.data)
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user is not None:
                return Response({
                    'status': True,
                    'token': str(Token.objects.get_or_create(user=user)[0]),
                    'user': UserSerializer(instance=user).data
                })

            return Response({
                'status': False,
                'message': 'Invalid Credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'status': False,
            'message': 'Invalid Request arguments'
        }, status=status.HTTP_400_BAD_REQUEST)


class DevicesView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get(request):
        return Response({'success': True, 'devices': UserDeviceSerializer(UserDevice.objects.all(), many=True).data})


class DeviceReadingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        device_no = self.request.GET.get('device_no')
        if device_no is not None:
            readings = Reading.objects.filter(device=device_no).order_by('-created_at')
            if readings.count() > 0:
                return Response({
                    'status': True,
                    'reading': ReadingSerializer(readings.first(), many=False).data
                })

            return Response({
                'status': True,
                'reading': {
                    'temperature': 0,
                    'ammonia': 0,
                    'turbidity': 0,
                    'ph': 0,
                    'dissolved_oxygen': 0
                }
            })

        return Response({
            'status': False,
            'message': 'Device not found'
        }, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def post(request):
        serializer = ReadingPostSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            reading = serializer.save()
            PostToReadingChannel(ReadingSerializer(instance=reading).data)
            message = ''
            if reading.temperature > 28 or reading.temperature < 24:
                message += f"Temp: {reading.temperature}C - (OP)\n"
            if reading.ph < 5.5 or reading.ph > 8.5:
                message += f"PH: {reading.ph} - (OP)"
            if len(message) > 0:
                pass
                send_sms('255624351398', message)
            return Response({
                'status': True,
            })
        return Response({
            'status': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class GetUserFromTokenView(APIView):
    @staticmethod
    def get(request):
        return Response({
            'success': True,
            'token': str(Token.objects.get_or_create(user=request.user)[0]),
            'user': UserSerializer(instance=request.user, many=False).data
        })


class SwitchView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        print(request.data)
        send_sms('255659787272', f"#{request.data['message']}")

        return Response({'success': True})


class ListDevicesView(generics.ListAPIView):
    search_fields = ['description', 'amount']
    filter_backends = (filters.SearchFilter,)
    serializer_class = UserDeviceSerializer
    pagination_class = StandardResultsSetPagination
    queryset = UserDevice.objects.all()


class DeviceDetailsView(APIView):
    @staticmethod
    def get(request, pk):
        try:
            device = UserDevice.objects.get(id=pk)
            return Response({'success': True, 'data': UserDeviceSerializer(instance=device, many=False).data})
        except UserDevice.DoesNotExist:
            return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)


class ListDevicesReadingsView(generics.ListAPIView):
    search_fields = ['']
    filter_backends = (filters.SearchFilter,)
    serializer_class = ReadingSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Reading.objects.all()


# WEB App

def login_request(request):
    if request.method == "POST":
        print(request.POST)
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                found_user = User.objects.get(username=username)
                print(found_user)
            except User.DoesNotExist:
                messages.error(request, "User does not exist")
                return redirect('/login')

            user = authenticate(username=username, password=password)
            if user is not None:
                print('Authentication successful')
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("/")
            else:
                messages.error(request, "Invalid username or password.")
                return redirect('/login')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('/login')


class DashboardView(TemplateView):
    template_name = "index.html"
    login_url = "login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['totalUsers'] = User.objects.all().count()  # Get all users count
        context['totalDevices'] = UserDevice.objects.all().count()  # Get all users count

        readings = Reading.objects.all().order_by('-created_at')
        readings_data = ReadingSerializer(readings.first(), many=False).data if readings.count() > 0 else {
           'temperature': 0,
           'ammonia': 0,
           'turbidity': 0,
           'ph': 0,
           'dissolved_oxygen': 0

        }
        context['readings'] = readings_data  # Get all users count

        return context


class ReadingsView(TemplateView):
    template_name = "readings.html"
    login_url = "login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readings'] = Reading.objects.all()  # Get all objectives
        return context


def logout_user(request):
    logout(request)
    return redirect('/login')


def export_excel_data(request):
    # Fetch the data you want to export
    columns = ['temperature', 'turbidity', 'ph']  # Replace with your model fields

    # Generate and return the Excel file
    return Reading.export_data_to_excel(columns, filename='Readings.xlsx')
