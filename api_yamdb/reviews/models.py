from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.utils.translation import gettext_lazy as _

from api_yamdb.settings import MAX_CHARS


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = 'admin', _('Администратор')
        MODERATOR = 'moderator', _('Модератор')
        USER = 'user', _('Пользователь')

    confirmation_code = models.CharField(
        'Код подтверждения', max_length=6, blank=True
    )
    username = models.CharField(
        'Псевдоним',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Недопустимый username',
            )
        ],
    )
    email = models.EmailField(
        'Емайл',
        max_length=254,
        unique=True,
        blank=False,
    )
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=Role.choices,
        default=Role.USER
    )
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    bio = models.TextField('Биография', default='', blank=True)
    is_admin = models.BooleanField('Админ', default=False)
    is_superuser = models.BooleanField('Суперюзер', default=False)
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_moderator(self):
        return self.is_superuser or self.role == self.Role.MODERATOR

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.Role.ADMIN

    def __str__(self):
        return f'{self.username}  {self.email}'


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор категории'
    )

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор жанра'
    )

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


def validate_year(value):
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError('Ахтунг! Произведение из будущего!')
    return value


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения'
    )
    # Артем, здесь мы подумали, что может лучше использовать
    # данный тип поля, но в то же время, произведения могут ведь
    # быть и до Н.Э. :)
    year = models.PositiveIntegerField(
        validators=(validate_year,),
        verbose_name='Год создания произведения'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        verbose_name='Категория произведения'
    )
    genre = models.ManyToManyField(Genre)

    class Meta:
        ordering = ('name', 'year',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def display_genres(self):
        """
        Создает строку из имен жанров. Нужна для отображения в админке.
        """
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genres.short_description = 'Жанры произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    score = models.IntegerField(
        validators=(
            MaxValueValidator(10, 'Оценка не должна превышать 10'),
            MinValueValidator(1, 'Оценка не должна быть меньше 1'),
        )
    )
    pub_date = models.DateTimeField(
        'Дата создания', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_author_title'
            ),
        )

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата создания', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:MAX_CHARS]
