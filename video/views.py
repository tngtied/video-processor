import json
import os
import logging
import asyncio

from asgiref.sync import sync_to_async

from .models import Video
from django.views import View
from django.http import JsonResponse
from django.conf import settings

from rest_framework.response import Response

from . import utils
from .serializers import FileUploadSerializer, EncodeSerializer

logger = logging.getLogger('django.server')
VIDEO_EXTENSION = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'mpeg', 'mpg', 'm4v', '3gp']


class UploadView(View):
    def post(self, request):
        file_serializer = FileUploadSerializer(data=request.data)
        if not file_serializer.is_valid():
            return Response({'success': False, 'video_id': None, 'message': '올바른 파일을 첨부해주세요'}, status=400)
        temporary_video = file_serializer.validated_data.file
        video = Video.objects.create()
        video_path = f"{video.id}.{temporary_video.name.split('.')[-1]}"
        with open(os.path.join(settings.MEDIA_ROOT, video_path), 'wb+') as destination:
            for chunk in temporary_video.chunks():
                destination.write(chunk)
        width, height = utils.get_video_resolution(os.path.join(settings.MEDIA_ROOT, video_path))
        logger.info('title: '+''.join(temporary_video.name.split('.')[:-1]))
        Video.objects.select_for_update().filter(id=video.id).update(
            title=''.join(temporary_video.name.split('.')[:-1]),
            video=video_path,
            format=temporary_video.name.split('.')[-1],
            resolution=f'{width}x{height}'
        )
        return JsonResponse({'success': True, 'video_id': video.id, 'message': "비디오 업로드가 완료되었습니다."})

# Create your views here.
class EncodeView(View):
    async def post(self, request):
        encode_serializer = EncodeSerializer(data=request.data)
        if not encode_serializer.is_valid():
            return JsonResponse({'success': False, 'message': '필수 항목을 입력해주세요.'}, status=400)
        output_video_id = (await sync_to_async(Video.objects.create)()).id
        asyncio.ensure_future(utils.process_video(input_video_id=encode_serializer.validated_data['video_id'],
                                                  output_video_id=output_video_id,
                                                  resolution=encode_serializer.validated_data['resolution'],
                                                  format=encode_serializer.validated_data['format']))
        logger.info(f"Returning JsonResponse")
        return JsonResponse({'success': True, 'video_id':output_video_id, 'message': '인코딩 작업을 시작합니다.'})