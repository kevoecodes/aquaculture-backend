from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from aqua.models import Reading, Device
from aqua.serializers import LoginSerializer, UserSerializer, ReadingSerializer, ReadingPostSerializer, \
    UserDeviceSerializer
from aqua.sms import send_sms
from aqua.socket.managers import PostToReadingChannel


class LoginView(APIView):
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
        return Response({'success': True, 'devices': UserDeviceSerializer(instance=Device.objects.all()).data})


class DeviceReadingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        device_no = self.request.GET.get('device_no')
        if device_no is not None:
            readings = Reading.objects.filter(device__device_no=device_no).order_by('-created_at')
            if readings.count() > 0:
                return Response({
                    'status': True,
                    'reading': ReadingSerializer(readings.first(), many=True).data
                })

            return Response({
                'status': True,
                'reading': {
                    'temperature': 0,
                    'ammonia': 0,
                    'turbidity': 0,
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
        if serializer.is_valid():
            reading = serializer.save()
            PostToReadingChannel(ReadingSerializer(instance=reading).data)
            if reading.temperature > 40 or reading.temperature < 16:
                message = f"Temperature {reading.temperature} C is out of range"
                send_sms('255624351398', message)
            return Response({
                'status': True,
            })
        return Response({
            'status': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
