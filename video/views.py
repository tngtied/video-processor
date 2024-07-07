from .models import Video
from django.views import View
from django.http import JsonResponse
from django.conf import settings
import json
import os
from . import utils
import logging
from asgiref.sync import sync_to_async
import asyncio

logger = logging.getLogger('django.server')
VIDEO_EXTENSION = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'mpeg', 'mpg', 'm4v', '3gp']


class UploadView(View):
    def post(self, request):
        logger.info('UploadView POST')
        if 'video' not in request.FILES:
            return JsonResponse({'success': False, 'message': '비디오 파일을 첨부해주세요.'}, status=400)
        temporary_video = request.FILES['video']
        logger.info(f"video.name.split('.')[-1] {temporary_video.name.split('.')[-1]}")
        if temporary_video.name.split('.')[-1] not in VIDEO_EXTENSION:
            return JsonResponse({'success': False, 'message': '올바른 비디오 파일을 첨부해주세요.'}, status=400)
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
        body = json.loads(request.body)
        video_id = body['video_id']
        logger.info(f"body['resolution'] {body['resolution']}")
        resolution = body['resolution']
        format = body['format']
        if not video_id or (not resolution and not format):
            return JsonResponse({'success': False, 'message': '필수 항목을 입력해주세요.'}, status=400)
        output_video_id = (await sync_to_async(Video.objects.create)()).id
        asyncio.ensure_future(utils.process_video(input_video_id=video_id, output_video_id=output_video_id, resolution=resolution, format=format))
        logger.info(f"Returning JsonResponse")
        return JsonResponse({'success': True, 'video_id':output_video_id, 'message': '인코딩 작업을 시작합니다.'})

class FrameView(View):
    def get(self, request, video_id):
        video = Video.objects.get(id=video_id)
        if not video:
            return JsonResponse({'success': False, 'message': '해당 비디오를 찾을 수 없습니다.'}, status=404)
        # TODO 프레임 추출 로직 짜기
        return JsonResponse({'success': True, 'message': '프레임을 추출합니다.'})