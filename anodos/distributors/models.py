import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class DistributorManager(models.Manager):

    def take(self, name, **kwargs):
        if not name:
            return None

        try:
            o = self.get(name=name)

        except Distributor.DoesNotExist:
            o = Distributor()
            o.name = name[:512]
            o.save()

        return o


class Distributor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=512, unique=True)

    objects = DistributorManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['name']


class CategoryManager(models.Manager):

    def take(self, distributor, name, parent=None, **kwargs):
        if not distributor or not name:
            return None
        try:
            o = self.get(distributor=distributor, name=name)
        except Category.DoesNotExist:
            o = Category()
            o.distributor = distributor
            o.article = kwargs.get('article', None)
            o.name = name
            o.parent = parent
            if parent is None:
                o.level = 0
            else:
                o.level = parent.level + 1

        o.save()
        return o


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    article = models.CharField(max_length=512, null=True, default=None, db_index=True)
    name = models.TextField(db_index=True)

    parent = models.ForeignKey('Category', null=True, default=None,
                               on_delete=models.CASCADE, related_name='+')
    level = models.IntegerField(default=0)

    created = models.DateTimeField(default=timezone.now)

    objects = CategoryManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['created']
