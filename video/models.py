from django.db import models

# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to='videos/')
    format = models.CharField(max_length=10)
    resolution = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True)
    def __str__(self):
        return f"{self.title}.{self.format}"

class Subtitle(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    subtitle = models.FileField(upload_to='subtitles/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.video.title

