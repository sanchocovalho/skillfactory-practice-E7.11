from django.db import models
from django.conf import settings
from datetime import datetime

class Comment(models.Model):
    author = models.CharField(
        verbose_name = u"Автор комментария",
        max_length=50
        )
    content = models.TextField(
        verbose_name = u'Комментарий'
        )
    created = models.DateTimeField(
        verbose_name = u'Дата публикации',
        auto_now_add=True
        )
    updated = models.DateTimeField(
        verbose_name = u'Обновлено',
        auto_now=True
        )
    advert = models.ForeignKey(
        'Advert',
        on_delete=models.CASCADE,
        blank=True,
        verbose_name = u'Объявление',
        related_name = 'comments'
        )

    class Meta:
        verbose_name = u'Комментарий'
        verbose_name_plural = u'Комментарии'

    def __str__(self):
        time = datetime.strftime(self.created, '%d-%m-%Y %H:%M:%S')
        return f'{self.author} : {time} : {self.advert.title}'


class Category(models.Model):
    name = models.CharField(
        verbose_name = u'Название категории',
        max_length=255,
        blank=True
        )

    class Meta:
        verbose_name = u'Категория'
        verbose_name_plural = u'Категории'

    def __str__(self):
        return self.name

class Advert(models.Model):
    title = models.CharField(
        verbose_name = u'Название объявления',
        max_length=255,
        blank=True
        )
    content = models.TextField(
        verbose_name = u'Содержание объявления',
        help_text = u'Обязательное поле'
        )
    tags = models.CharField(
        verbose_name = u'Теги',
        max_length=255
        )
    created = models.DateTimeField(
        verbose_name = u'Дата публикации',
        auto_now_add=True
        )
    updated = models.DateTimeField(
        verbose_name = u'Обновлено',
        auto_now=True
        )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
        verbose_name = u'Категория',
        related_name = 'adverts'
        )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
        verbose_name = u'Автор объявления',
        related_name = 'adverts'
        )
    photo = models.ImageField(
        verbose_name='Фото',
        upload_to='photos',
        blank=True
        )

    class Meta:
        verbose_name = u"Объявление"
        verbose_name_plural = u"Объявления"

    def __str__(self):
        time = datetime.strftime(self.created, '%d-%m-%Y %H:%M:%S')
        return f'{self.title} : {time}'

