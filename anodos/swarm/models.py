import os
import uuid
from django.db import models
from django.conf import settings
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

    def take(self, source=None, url=None):

        if url is None:
            return None

        try:
            o = self.get(source=source, url=url)
        except SourceData.DoesNotExist:
            o = SourceData()
            o.source = source
            o.url = url
            o.save()

        # Проверяем наличие уже скачанного файла
        if o.source is None:
            file_name = '{}swarm/{}/{}'.format(settings.MEDIA_ROOT, 'None', o.url)
        else:
            file_name = '{}swarm/{}/{}'.format(settings.MEDIA_ROOT, o.source.name, o.url)

        if os.path.isfile(file_name):
            o.file_name = file_name
            o.save()

        return o


class SourceData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    source = models.ForeignKey('Source', null=True, default=None,
                               on_delete=models.CASCADE, related_name='+')
    url = models.TextField(null=True, default=None, db_index=True)
    file_name = models.TextField(null=True, default=None)
    content = models.TextField(null=True, default=None)

    created = models.DateTimeField(default=timezone.now)
    parsed = models.DateTimeField(null=True, default=None)

    objects = SourceDataManager()

    def save_file(self, data_):
        self.file_name = '{}swarm/{}/{}'.format(settings.MEDIA_ROOT, self.source.name, self.url)
        directory = '/'
        for dir_ in self.file_name.split('/')[:-1]:
            directory = '{}/{}'.format(directory, dir_)
            if not os.path.exists(directory):
                os.makedirs(directory)
        if type(data_) == str:
            with open(self.file_name, "w") as f:
                f.write(data_)
        else:
            with open(self.file_name, "wb") as f:
                f.write(data_.getbuffer())
        self.save()

    def load_file(self):
        if self.file_name is None:
            self.file_name = '{}swarm/{}/{}'.format(settings.MEDIA_ROOT, self.source.name, self.url)
        f = open(self.file_name, 'r')
        content = f.read()
        return content

    def set_parsed(self):
        self.parsed = timezone.now()
        self.save()

    def __str__(self):
        if self.url:
            return 'SourceData: {}'.format(self.url)
        else:
            return 'SourceData: {}'.format(self.source.name)

    class Meta:
        ordering = ['created']


class DataManager(models.Manager):

    @staticmethod
    def add(source_data, content_type, content):
        o = Data()
        o.source_data = source_data
        o.content_type = content_type
        o.save()

        o.file_name = '{}swarm/data/{}/{}.{}'.format(settings.MEDIA_ROOT,
                                                     o.content_type,
                                                     o.id,
                                                     o.content_type)
        directory = '/'
        for dir_ in o.file_name.split('/')[:-1]:
            directory = '{}/{}'.format(directory, dir_)
            if not os.path.exists(directory):
                os.makedirs(directory)
        with open(o.file_name, "wb") as f:
            f.write(content)
        o.save()

        return o


class Data(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_data = models.ForeignKey('SourceData', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    content_type = models.TextField(null=True, default=None, db_index=True)
    file_name = models.TextField(null=True, default=None, db_index=True)

    created = models.DateTimeField(default=timezone.now)
    parsed = models.DateTimeField(null=True, default=None)

    def __str__(self):
        'Data: {}'.format(self.file_name)

    class Meta:
        ordering = ['created']

    objects = DataManager()


class OrganisationManager(models.Manager):

    def take(self, ogrn, **kwargs):
        if not ogrn:
            return None

        try:
            o = self.get(ogrn=ogrn)

        except Organisation.DoesNotExist:
            o = Organisation()
            o.ogrn = ogrn
            o.name = kwargs.get('name', None)
            o.inn = kwargs.get('inn', None)
            o.save()

        return o


class Organisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ogrn = models.TextField(unique=True)
    name = models.TextField(null=True, default=None)
    inn = models.TextField(null=True, default=None)

    created = models.DateTimeField(default=timezone.now)

    objects = OrganisationManager()

    def __str__(self):
        return f"{self.name} ({self.ogrn} {self.inn})"

    class Meta:
        ordering = ['-created']


class ProductManager(models.Manager):

    def take(self, register_number, **kwargs):
        if not register_number:
            return None

        try:
            o = self.get(register_number=register_number)
            o.new = False

        except Product.DoesNotExist:
            o = Product()
            o.register_number = register_number
            o.organisation = kwargs.get('organisation', None)
            o.name = kwargs.get('name', None)
            o.okpd2 = kwargs.get('okpd2', None)
            o.tnved = kwargs.get('tnved', None)
            o.name_of_regulation = kwargs.get('name_of_regulation', None)
            o.save()
            o.new = True

        return o


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    register_number = models.TextField(unique=True)
    organisation = models.ForeignKey('Organisation',
                                     null=True,
                                     default=None,
                                     on_delete=models.CASCADE,
                                     related_name='+')

    name = models.TextField(null=True, default=None)
    okpd2 = models.TextField(null=True, default=None)
    tnved = models.TextField(null=True, default=None)
    name_of_regulation = models.TextField(null=True, default=None)

    created = models.DateTimeField(default=timezone.now)

    objects = ProductManager()

    def __str__(self):
        return f"{self.register_number} {self.name}"

    class Meta:
        ordering = ['-created']
