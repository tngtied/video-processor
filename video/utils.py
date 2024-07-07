from .models import Video
import os
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
import cv2
import logging
import asyncio

logger = logging.getLogger('django.server')

def get_video_resolution(video_path):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height

async def process_video(input_video_id, output_video_id, resolution, format):
    input_video = await sync_to_async(Video.objects.get)(id=input_video_id)
    resolution = resolution if resolution else input_video.resolution,
    format = format if format else input_video.format
    input_path = os.path.join(settings.MEDIA_ROOT, f"{input_video.id}.{input_video.format}")
    output_path = os.path.join(settings.MEDIA_ROOT, f'{output_video_id}.{format}')

    cap = cv2.VideoCapture(input_path)
    if format == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    elif format == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    else:
        await send_sse_message(output_video_id, False, "지원하지 않는 포맷입니다.")
        await sync_to_async(Video.objects.filter(id=output_video_id).delete)()

    width, height = resolution.split('x')
    out = cv2.VideoWriter(output_path, fourcc, 30, (width, height))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, (int(width), int(height)))
        out.write(resized_frame)
    cap.release()
    out.release()

    output_video = await sync_to_async(Video.objects.select_for_update().filter(id=output_video_id).update)(
        title=input_video.title,
        video=f'{output_video_id}.{format}',
        format=format,
        resolution=resolution
    )
    await send_sse_message(output_video.id, True, "비디오 인코딩이 완료되었습니다.")

async def send_sse_message(video_id, success, message=None):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(f"group_{video_id}", {
        'type': 'send_message',
        'success': success,
        'message': message
    })
    logger.info(f"send_sse_message invoked: {video_id}, {success}, {message}")