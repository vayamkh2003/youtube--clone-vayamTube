from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import Channel, Video

class SimpleTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status(self):
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)

    def test_upload_requires_login(self):
        res = self.client.get(reverse('upload-video'))
        self.assertIn(res.status_code, (302, 301))  # redirected to login

    def test_search_returns_video(self):
        user = User.objects.create_user(username='tester', password='pass')
        channel = Channel.objects.create(user=user, name='TestChannel')

        # create a dummy video and thumbnail
        thumbnail = SimpleUploadedFile('thumb.jpg', b'fake-image-content', content_type='image/jpeg')
        video_file = SimpleUploadedFile('video.mp4', b'fake-video-content', content_type='video/mp4')

        video = Video.objects.create(user=user, channel=channel, video_file=video_file, title='UniqueTitle', thumbnail=thumbnail)

        res = self.client.post(reverse('searched'), {'s': 'UniqueTitle'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'UniqueTitle')
