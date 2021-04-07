import os
import uuid
from django.db import models
from django.conf import settings


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
