from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        for i in range(10):
            cls.group = Group.objects.create(
                title='Тестовая группа: ' + str(i),
                slug='test-slug-' + str(i),
                description='Тестовое описание группы четрые пять',
            )
            Post.objects.create(
                text='Тестовый пост_' + str(i),
                author=cls.user,
                group=cls.group,
            )
        cls.group = Group.objects.first()
        cls.post = Post.objects.first()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTest.user)

    def test_about_page_uses_correct_template(self):
        path_name_template_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTest.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTest.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewTest.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:posts',
                kwargs={'post_id': PostViewTest.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for path_name, template in path_name_template_names.items():
            with self.subTest(path_name=path_name):
                response = self.authorized_client.get(path_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Вызываемый шаблон не соответствует ожидаемому'
                )

    def test_index_used_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        posts = Post.objects.order_by('-pub_date')[:10]
        for i in range(len(posts)):
            self.assertEqual(response.context['page_obj'][i], posts[i])

    def test_post_list_filter_group_context(self):
        posts = PostViewTest.group.posts.order_by('-pub_date')[:10]
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTest.group.slug}
            )
        )
        for i in range(len(posts)):
            self.assertEqual(response.context['page_obj'][i], posts[i])

    def test_post_list_filter_user(self):
        posts = PostViewTest.user.posts.order_by('-pub_date')[:10]
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTest.user.username}
            )
        )
        for i in range(len(posts)):
            self.assertEqual(response.context['page_obj'][i], posts[i])

    def test_one_post_filter_id(self):
        """Проверка работы функции вывода
        нужного поста на станицу
        """
        post_id = PostViewTest.post.pk
        posts = Post.objects.get(pk=post_id)
        response = self.authorized_client.get(
            reverse(
                'posts:posts', kwargs={'post_id': post_id}
            )
        )
        self.assertEqual(response.context['post'], posts)

    def test_group_posts(self):
        """ Пост одной группы не должен отображаться на
            странице другой группы
        1.  Если создать один пост для группы, то на странице
            группы будет виден только один пост
        2.  Если создать некое количество постов группы, то
            количество постов на странице группы не будет отличаться
        3.  Если создать один пост для группы, то на странице
            группы будет отображаться тот самый пост
            с текстом и группой
        """
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTest.group.slug}
            )
        )
        self.assertEqual(
            len(response.context['page_obj']),
            1
        )
        self.assertEqual(
            len(response.context['page_obj']),
            PostViewTest.group.posts.count()
        )

        post_for_check = PostViewTest.group.posts.first()
        self.assertEqual(
            response.context['page_obj'][0].text,
            post_for_check.text
        )
        self.assertEqual(
            response.context['page_obj'][0].group.pk,
            post_for_check.group.pk
        )
