from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from aqua.models import Reading
from aqua.serializers import ReadingSerializer


class ReadingConsumer(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        self.deviceNo = self.scope['path_remaining']
        self.thread_name = f"thread_device_{self.deviceNo}"
        await self.channel_layer.group_add(
            self.thread_name,
            self.channel_name
        )
        await self.accept()
        device_data = await self.fetch_device_data()

        await self.send_json(device_data)

    async def websocket_receive(self, event):
        print("Message: ", event['text'])

        await self.channel_layer.group_send(
            self.thread_name,
            {
                "type": "send.message",
                "data": event['text']
            }
        )

    async def send_message(self, event):
        print('messages', event)

        await self.send_json(event['data'])

    async def websocket_disconnect(self, event):
        print("disonnected", event)
        # OnlineUpdate(False, self.deviceNo)
        await self.channel_layer.group_discard(
            self.thread_name,
            self.channel_name
        )
        await self.disconnect(event['code'])
        raise StopConsumer()

    @database_sync_to_async
    def fetch_device_data(self):
        readings = Reading.objects.filter(device__device_no=self.deviceNo).order_by('-created_at')

        if readings.count() > 0:
            return {
                'reading': ReadingSerializer(readings.first(), many=False).data
            }

        return {
            'reading': {
                'id': 0,
                'device_no': self.deviceNo,
                'temperature': 0,
                'ammonia': 0,
                'turbidity': 0,
                'dissolved_oxygen': 0
            }
        }
