from django.urls import re_path
from video import consumers

websocket_urlpatterns = [
    re_path(r'ws/video/sse/(?P<user_id>\w+)/$', consumers.VideoConsumer.as_asgi()),
]