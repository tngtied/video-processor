from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger('django.server')
class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user_id = self.scope['url_route']['kwargs']['user_id']
            self.group_name = f"group_{self.user_id}"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        except Exception as e:
            logger.info(f"Exeption raised during consumers.py connect: {e}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


    async def send_message(self, event):
        await self.send(text_data=json.dumps({
            'success': event['success'],
            'video_id': event['video_id'],
            'message': event['message']
        }))
