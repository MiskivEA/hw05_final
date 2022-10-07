from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()


class CommentViewTest(TestCase):
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

        cls.comment = Comment.objects.bulk_create([
            Comment(
                text='comment test ' + str(i),
                author=cls.user,
                post=cls.post
            )for i in range(10)
        ])

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(CommentViewTest.user)

    def test_only_authorized_user_can_comment(self):
        """Тестирование редиректов.
        Неавторизованый пользователь при попытке
        оставить комментарий будет перенаправлен
        на страницу авторизации
        """
        post_id = CommentViewTest.post.pk
        form_data = {'text': 'new comment 2'}
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post_id}
            ),
            data=form_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{post_id}/comment/'
        )

    def test_created_comment_exists(self):
        """ Проверка добавления коментария в БД """
        post_id = CommentViewTest.post.pk
        form_data = {'text': 'new comment 3'}
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post_id}
            ),
            data=form_data
        )
        self.assertTrue(
            Comment.objects.filter(text=form_data['text']).exists())

    def test_created_comment_shows_on_page(self):
        """ Проверка отображения комментария на странице нужного поста """
        post_id = CommentViewTest.post.pk
        form_data = {'text': 'new comment 3'}
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post_id}
            ),
            data=form_data
        )
        response = self.authorized_client.get(
            reverse(
                'posts:posts',
                kwargs={'post_id': post_id}
            )
        )
        self.assertEqual(
            response.context['comments'].first(),
            Comment.objects.first()
        )
