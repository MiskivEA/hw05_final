import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ..models import Post, Group

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImagesViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='test-image.jpeg',
            content=cls.test_image,
            content_type='image/jpeg'
        )
        cls.user = User.objects.create_user(username='test_admin')
        cls.group = Group.objects.create(
            title='Test group-2433245',
            slug='test-slug-24353',
            description='test group description-242343q54'
        )
        cls.post = Post.objects.create(
            text='тестовый пост три четыре пять',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(ImagesViewTest.user)

    def test_images_context_index_profile_group(self):
        check_urls = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': ImagesViewTest.user.username}),
            reverse('posts:group_list', kwargs={'slug': ImagesViewTest.post.group.slug}),
        ]
        for url in check_urls:
            response = self.authorized_client.get(url)
            self.assertEqual(response.context['page_obj'][0].image, Post.objects.first().image)

    def test_posts_image(self):
        response = self.authorized_client.get(reverse('posts:posts', kwargs={'post_id': ImagesViewTest.post.pk}))
        self.assertEqual(response.context['post'].image, Post.objects.first().image)
