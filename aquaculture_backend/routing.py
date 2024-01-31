from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path

from aqua.socket.consumers import ReadingConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                re_path(r"^ws/device-reading/(?P<device_no>)", ReadingConsumer.as_asgi()),
            ]
        )
    )
})
