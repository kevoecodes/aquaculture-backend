from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class PostToReadingChannel:
    def __init__(self, data):
        self.channel_name, self.data = f"thread_device_{data['device_no']}", data
        self.post_to_channel()

    def post_to_channel(self):
        print(self.data)
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(self.channel_name, {
            "type": "send.message",
            "data": {
                'reading': self.data
            }
        })

