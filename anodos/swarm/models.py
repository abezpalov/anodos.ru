import uuid
from django.db import models
from django.utils import timezone


class SourceManager(models.Manager):

    def take(self, name, **kwargs):
        if not name:
            return None

        try:
            o = self.get(name=name)

        except Source.DoesNotExist:
            o = Source()
            o.name = name[:512]
            o.login = kwargs.get('login', None)
            o.password = kwargs.get('password', None)
            o.save()

        return o


class Source(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=512, unique=True)
    login = models.TextField(null=True, default=None)
    password = models.TextField(null=True, default=None)

    objects = SourceManager()

    def __str__(self):
        return "Source: {}".format(self.name)

    class Meta:
        ordering = ['name']


class SourceDataManager(models.Manager):

    def take(self, source, url=None, **kwargs):
        if not source:
            return None

        try:
            o = self.get(source=source, url=url)

        except SourceData.DoesNotExist:
            o = SourceData()
            o.source = source
            o.url = url
            o.save()

        return o


class SourceData(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    source = models.ForeignKey('Source', null=True, default=None,
                               on_delete=models.CASCADE, related_name='+')
    url = models.TextField(null=True, default=None)
    file_name = models.TextField(null=True, default=None)

    objects = SourceDataManager()

    def __str__(self):
        if self.url:
            return '{}/{}'.format(self.source.name, self.url)
        else:
            return '{}'.format(self.source.name)

    class Meta:
        ordering = ['url']