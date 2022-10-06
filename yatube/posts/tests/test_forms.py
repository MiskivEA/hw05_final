import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_admin')
        cls.group = Group.objects.create(
            title='Test group-2433245',
            slug='test-slug-24353',
            description='test group description-242343q54'
        )
        cls.post = Post.objects.create(
            text='тестовый пост три четыре пять',
            author=cls.user,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)

    def test_form_create(self):
        """Тестирование создания форм.
        1. Проверка создания поста по факту уведичения их количества в БД
        2. Проверка редиректа после создания поста
        3. Проверка данных после создания поста
        """
        posts_count_1 = Post.objects.count()
        test_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test-image.jpeg',
            content=test_image,
            content_type='image/jpeg'
        )
        form_data = {
            'text': 'Тестовый текст из формы',
            'group': PostFormTest.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        posts_count_2 = Post.objects.count()
        self.assertEqual(posts_count_1 + 1, posts_count_2)
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': PostFormTest.user.username})
        )
        self.assertEqual(
            response.context['page_obj'][0].text,
            Post.objects.first().text
        )
        self.assertEqual(
            response.context['page_obj'][0].author.username,
            Post.objects.first().author.username
        )
        self.assertEqual(
            response.context['page_obj'][0].group.pk,
            Post.objects.first().group.pk
        )
        self.assertEqual(
            response.context['page_obj'][0].image,
            Post.objects.first().image
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст из формы',
                image='posts/test-image.jpeg'
            ).exists()
        )

    def test_form_edit(self):
        """Тестирование формы редактирования поста.
        Сравнение данных поста после редактирования
        с данными, переданными в форму
        """
        post_id = PostFormTest.post.pk
        form_data = {
            'text': 'Текст поста после редактирования',
            'group': PostFormTest.group.pk
        }
        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post_id}
            ),
            data=form_data
        )
        post = Post.objects.get(pk=post_id)
        self.assertEqual(
            post.text,
            form_data['text']
        )
        self.assertEqual(
            post.group.pk,
            form_data['group']
        )
