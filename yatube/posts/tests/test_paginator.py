from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='test group',
            slug='test-slug',
            description='test description'
        )

        Post.objects.bulk_create([
            Post(
                text='Тестовый пост-' + str(i),
                author=cls.user,
                group=cls.group
            )
            for i in range(13)
        ])

    def setUp(self):
        self.client = Client()
        self.client.force_login(PaginatorViewTest.user)

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewTest.user.username}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewTest.user.username}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewTest.group.slug}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewTest.group.slug}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
