from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class CacheTest(TestCase):
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
            text='testpost',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(CacheTest.user)

    def test_cache_index(self):
        """ Тестирование работы кэша.
        1.  Запрашиваю главную страницу, считаю количество объектов,
            которые переданы в нее
        2.  Убеждаюсь, что количество объектов в БД равно 1,
            как и количество объектов переданных на страницу
            при запросе
        3.  Удаляю запись из БД, повторяю запрос к главной странице,
            убеждаюсь, что в БД больше нет записей, но не смотря на это
            в контенте страницы есть данные поста
        4.  После очистки кэша никаких данных удаленного поста на
            странице больше нет
        """
        response = self.authorized_client.get(reverse('posts:index'))
        count_page_objects = len(response.context['page_obj'])
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(count_page_objects, 1)

        CacheTest.post.delete()

        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn(CacheTest.post.text, str(response.content))

        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotIn(CacheTest.post.text, str(response.content))
