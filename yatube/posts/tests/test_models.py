from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовая слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='12345678901234567890',
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(str(PostModelTest.group), PostModelTest.group.title)
        self.assertEqual(str(PostModelTest.post), PostModelTest.post.text[:15])

    def test_models_verbose_and_help_names(self):
        """Проверяем, что у полей отображается нужные лейблы и подсказки"""
        fields = {
            'text': {
                'verbose_name': 'Текст поста',
                'help_text': 'Текст нового поста'
            },
            'group': {
                'verbose_name': 'Группа',
                'help_text': 'Группа, к которой будет относиться пост'
            }
        }

        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected_value['verbose_name'],
                    'Неверное имя поля'
                )
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text,
                    expected_value['help_text'],
                    'Неверное имя подсказки'
                )
