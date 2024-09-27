from rest_framework import serializers

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class EncodeSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()
    resolution = serializers.CharField(max_length=50)
    format = serializers.CharField(max_length=50)