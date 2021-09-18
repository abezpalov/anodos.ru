import os
import uuid
import requests as r
from django.db import models
from django.conf import settings
from django.utils import timezone


class CategoryManager(models.Manager):

    pass


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.TextField(db_index=True)
    description = models.TextField(default='')
    number = models.BigIntegerField(null=True, default=0)

    objects = CategoryManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['number', 'name']


class ArticleManager(models.Manager):
    pass


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(db_index=True)
    slug = models.TextField(db_index=True, null=True, default=None)
    content = models.TextField(null=True, default=None)
    description = models.TextField(null=True, default=None)

    created = models.DateTimeField(db_index=True, default=timezone.now)
    edited = models.DateTimeField(db_index=True, null=True, default=None)
    published = models.DateTimeField(db_index=True, null=True, default=None)

    objects = ArticleManager()

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['-created']


def to_slug(name):
    name = name.lower()
    name = name.strip()
    dictionary = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
                  'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm',
                  'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                  'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'cz', 'ш': 'sh', 'щ': 'scz',
                  'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'u', 'я': 'ja',
                  ',': '-', '?': '-', ' ': '-', '~': '-', '!': '-', '@': '-', '#': '-',
                  '$': '-', '%': '-', '^': '-', '&': '-', '*': '-', '(': '-', ')': '-',
                  '=': '-', '+': '-', ':': '-', ';': '-', '<': '-', '>': '-', '\'': '-',
                  '"': '-', '\\': '-', '/': '-', '№': '-', '[': '-', ']': '-', '{': '-',
                  '}': '-', 'ґ': '-', 'ї': '-', 'є': '-', 'Ґ': 'g', 'Ї': 'i', 'Є': 'e',
                  '—': '-'}

    for key in dictionary:
        name = name.replace(key, dictionary[key])

    while '--' in name:
        name = name.replace('--', '-')

    if name[0] == '-':
        name = name[1:]

    if name[-1] == '-':
        name = name[:-1]

    return name
