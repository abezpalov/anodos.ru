import os
import uuid
import requests as r
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.indexes import GinIndex


class ArticleManager(models.Manager):
    pass


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Article = models.ForeignKey('Article', null=True, default=None,
                                on_delete=models.SET_NULL, related_name='+')
    title = models.TextField(db_index=True)
    slug = models.TextField(db_index=True, null=True, default=None)
    path = models.TextField(db_index=True, null=True, default=None)
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


class CategoryManager(models.Manager):

    pass


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(db_index=True)

    parent = models.ForeignKey('Category', null=True, default=None,
                               on_delete=models.CASCADE, related_name='+')
    level = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    created = models.DateTimeField(default=timezone.now)

    objects = CategoryManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['created']


class VendorManager(models.Manager):

    pass


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(db_index=True)
    slug = models.TextField(null=True, default=None, db_index=True)

    objects = VendorManager()

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        self.slug = to_slug(name=self.name)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']


class UnitManager(models.Manager):

    pass


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(null=True, default=None, db_index=True)
    full_name = models.TextField(null=True, default=None, db_index=True)

    objects = UnitManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['name']


class CurrencyManager(models.Manager):

    pass


class Currency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=32, unique=True)

    name = models.TextField(null=True, default=None, db_index=True)
    full_name = models.TextField(null=True, default=None, db_index=True)

    objects = CurrencyManager()

    def __str__(self):
        return f'{self.key}'

    class Meta:
        ordering = ['key']


class PriceManager(models.Manager):

    pass


class Price(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    currency = models.ForeignKey('Currency', null=True, default=None,
                                 on_delete=models.CASCADE, related_name='+')

    created = models.DateTimeField(default=timezone.now)

    objects = PriceManager()

    def __str__(self):
        return f'{self.value} {self.currency}'

    @property
    def html(self):
        return f'{self.value}&nbsp;{self.currency}'

    class Meta:
        ordering = ['created']


class ProductManager(models.Manager):

    pass


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    part_number = models.TextField(null=True, default=None, db_index=True)
    vendor = models.ForeignKey('Vendor', null=True, default=None,
                               on_delete=models.CASCADE, related_name='+')
    category = models.ForeignKey('Category', null=True, default=None,
                                 on_delete=models.SET_NULL, related_name='+')
    search = models.TextField(null=True, default=None, db_index=True)

    name = models.TextField(null=True, default=None, db_index=True)
    short_name = models.TextField(null=True, default=None, db_index=True)
    name_rus = models.TextField(null=True, default=None, db_index=True)
    name_other = models.TextField(null=True, default=None, db_index=True)

    description = models.TextField(null=True, default=None)
    warranty = models.TextField(null=True, default=None)

    # Коды
    ean_128 = models.TextField(null=True, default=None, db_index=True)
    upc = models.TextField(null=True, default=None, db_index=True)
    pnc = models.TextField(null=True, default=None, db_index=True)
    hs_code = models.TextField(null=True, default=None, db_index=True)
    gtin = models.TextField(null=True, default=None, db_index=True)
    tnved = models.TextField(null=True, default=None, db_index=True)

    # Прослеживаемый товар
    traceable = models.BooleanField(null=True, default=None, db_index=True)

    # Цена, кондиционность и распродажа
    price = models.ForeignKey('Price', null=True, default=None,
                              on_delete=models.SET_NULL, related_name='+')
    unconditional = models.BooleanField(default=False, db_index=True)
    sale = models.BooleanField(default=False, db_index=True)
    promo = models.BooleanField(default=False, db_index=True)
    outoftrade = models.BooleanField(default=False, db_index=True)
    condition_description = models.TextField(null=True, default=None)

    # Количество и характеристики упаковки
    quantity = models.IntegerField(null=True, default=None)
    quantity_great_than = models.BooleanField(null=True, default=None, db_index=True)
    weight = models.DecimalField(max_digits=18, decimal_places=9, null=True, default=None)
    width = models.DecimalField(max_digits=18, decimal_places=9, null=True, default=None)
    height = models.DecimalField(max_digits=18, decimal_places=9, null=True, default=None)
    depth = models.DecimalField(max_digits=18, decimal_places=9, null=True, default=None)
    volume = models.DecimalField(max_digits=18, decimal_places=9, null=True, default=None)
    multiplicity = models.IntegerField(null=True, default=None)
    unit = models.ForeignKey('Unit', null=True, default=None,
                             on_delete=models.SET_NULL, related_name='+')

    # Контент
    content = models.TextField(null=True, default=None)
    content_loaded = models.DateTimeField(null=True, default=None)

    # Служебное
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(null=True, default=None)
    edited = models.DateTimeField(null=True, default=None)

    objects = ProductManager()

    def __str__(self):
        if self.vendor is None:
            return f'None [{self.part_number}] ({self.id})'
        else:
            return f'{self.vendor.name} [{self.part_number}] ({self.id})'

    def save(self, *args, **kwargs):
        if self.vendor:
            self.search = f'{self.name.lower()} ' \
                          f'{self.part_number.lower()} ' \
                          f'{self.vendor.name.lower()}'
        else:
            self.search = f'{self.name.lower()} ' \
                          f'{self.part_number.lower()}'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['vendor', 'part_number']
        indexes = [GinIndex(fields=['search'],
                            name='product_search_idx')]


class LocationManager(models.Manager):

    pass


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.TextField(null=True, default=None, db_index=True)
    description = models.TextField(null=True, default=None)

    objects = LocationManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['name']


class PartyManager(models.Manager):

    pass


class Party(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('Product', null=True, default=None,
                                on_delete=models.CASCADE, related_name='+')

    # Цены
    price = models.ForeignKey('Price', null=True, default=None,
                              on_delete=models.CASCADE, related_name='rel_party_price')
    price_in = models.ForeignKey('Price', null=True, default=None,
                                 on_delete=models.CASCADE, related_name='rel_party_price_in')
    price_out = models.ForeignKey('Price', null=True, default=None,
                                  on_delete=models.CASCADE, related_name='rel_party_price_out')
    price_out_open = models.ForeignKey('Price', null=True, default=None,
                                       on_delete=models.CASCADE, related_name='rel_party_price_out_open')
    must_keep_end_user_price = models.BooleanField(null=True, default=None, db_index=True)

    # Доступность
    location = models.ForeignKey('Location', null=True, default=None,
                                 on_delete=models.CASCADE, related_name='+')
    quantity = models.IntegerField(null=True, default=None)
    quantity_great_than = models.BooleanField(null=True, default=None, db_index=True)
    unit = models.ForeignKey('Unit', null=True, default=None,
                             on_delete=models.CASCADE, related_name='+')
    can_reserve = models.BooleanField(null=True, default=None, db_index=True)
    is_available_for_order = models.BooleanField(null=True, default=None, db_index=True)

    created = models.DateTimeField(default=timezone.now)

    objects = PartyManager()

    def __str__(self):
        return f'{self.product} | {self.quantity} on {self.location}'

    class Meta:
        ordering = ['created']


class ParameterGroupManager(models.Manager):

    pass


class ParameterGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(null=True, default=None, db_index=True)
    order = models.IntegerField(default=0)

    objects = ParameterGroupManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['order']


class ParameterManager(models.Manager):

    pass


class Parameter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey('ParameterGroup', null=True, default=None,
                              on_delete=models.CASCADE, related_name='+')
    name = models.TextField(null=True, default=None, db_index=True)
    description = models.TextField(null=True, default=None)
    order = models.IntegerField(default=0)

    objects = ParameterManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['order']


class ParameterValueManager(models.Manager):

    pass


class ParameterValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parameter = models.ForeignKey('Parameter', null=True, default=None,
                                  on_delete=models.CASCADE, related_name='+')

    value = models.TextField(null=True, default=None, db_index=True)
    unit = models.ForeignKey('Unit', null=True, default=None,
                             on_delete=models.CASCADE, related_name='+')

    created = models.DateTimeField(default=timezone.now, db_index=True)

    objects = ParameterValueManager()

    def __str__(self):
        if self.unit:
            return f'{self.product}: {self.parameter} = {self.value} {self.unit}'
        else:
            return f'{self.product}: {self.parameter} = {self.value}'

    class Meta:
        ordering = ['created']


class ProductImageManager(models.Manager):

    pass


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('Product', null=True, default=None,
                                on_delete=models.CASCADE, related_name='+')
    source_url = models.TextField(null=True, default=None, db_index=True)
    file_name = models.TextField(null=True, default=None)
    ext = models.TextField(null=True, default=None)

    created = models.DateTimeField(default=timezone.now, db_index=True)

    objects = ProductImageManager()

    @property
    def url(self):
        if self.file_name:
            return self.file_name.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
        else:
            return None

    def download_file(self):

        # Определяем имя файла
        if self.ext is None:
            self.ext = self.source_url.rpartition('.')[2]
        self.file_name = f'{settings.MEDIA_ROOT}distributors/products/photos/{self.id}.{self.ext}'

        # Загружаем фотографию
        result = r.get(self.source_url)

        directory = '/'
        for dir_ in self.file_name.split('/')[:-1]:
            directory = '{}/{}'.format(directory, dir_)
            if not os.path.exists(directory):
                os.makedirs(directory)
        with open(self.file_name, "wb") as f:
            f.write(result.content)
        self.save()

    def __str__(self):
        return f'{self.product}: {self.source_url}'

    class Meta:
        ordering = ['created']


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
