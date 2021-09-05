import os
import uuid
import requests as r
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

    def take(self, distributor, article=None, name=None, parent=None):
        if not distributor:
            return None
        if not article and not name:
            return None

        need_save = False

        if article:
            try:
                o = self.get(distributor=distributor, article=article)
            except Category.DoesNotExist:
                o = Category()
                o.distributor = distributor
                o.article = article
                o.name = name
                o.parent = parent
                need_save = True

            if name and o.name != name:
                o.name = name
                need_save = True
            if parent and o.parent != parent:
                o.parent = parent

            if o.parent is None:
                level = 0
            else:
                level = o.parent.level + 1

            if o.level != level:
                o.level = level
                need_save = True

            if o.name is None:
                o.name = o.article
                need_save = True

        else:
            print('Category.take not work on name')
            return None

        if need_save:
            o.save()

        return o

    def get_by_article(self, distributor, article):
        try:
            o = self.get(distributor=distributor, name__contains=f'[{article}]')
        except Category.DoesNotExist:
            return None
        return o


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    article = models.TextField(db_index=True, null=True, default=None)
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


class VendorManager(models.Manager):

    def take(self, distributor, name, **kwargs):
        if not distributor or not name:
            return None

        try:
            o = self.get(distributor=distributor, name=name)

        except Vendor.DoesNotExist:
            o = Vendor()
            o.distributor = distributor
            o.name = name
            o.save()

        return o


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(db_index=True)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    objects = VendorManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['name']


class ConditionManager(models.Manager):

    def take(self, distributor, name, **kwargs):
        if not distributor or not name:
            return None

        try:
            o = self.get(distributor=distributor, name=name)

        except Condition.DoesNotExist:
            o = Condition()
            o.distributor = distributor
            o.name = name
            o.save()

        return o


class Condition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(db_index=True)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    objects = ConditionManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['name']


class UnitManager(models.Manager):

    def take(self, key, **kwargs):
        if not key:
            return None

        try:
            o = self.get(key=key)

        except Unit.DoesNotExist:
            o = Unit()
            o.key = key[:32]
            o.save()

        if o.name is None:
            o.name = key
            o.save()

        return o


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=32, unique=True)

    name = models.TextField(null=True, default=None, db_index=True)
    print_name = models.TextField(null=True, default=None, db_index=True)

    objects = UnitManager()

    def __str__(self):
        return f'{self.key}'

    class Meta:
        ordering = ['key']


class ProductManager(models.Manager):

    def take_by_party_key(self, distributor, party_key, name, **kwargs):

        if not distributor or not party_key or not name:
            exit()
            return None

        need_save = False

        try:
            o = self.get(distributor=distributor, party_key=party_key)
        except Product.DoesNotExist:
            o = Product()
            o.distributor = distributor
            o.party_key = party_key
            o.name = name
            need_save = True

        # name
        if name is not None and name != o.name:
            o.name = name
            need_save = True

        # vendor
        vendor = kwargs.get('vendor', None)
        if vendor is not None and vendor != o.vendor:
            o.vendor = vendor
            need_save = True

        # category
        category = kwargs.get('category', None)
        if category is not None and category != o.category:
            o.category = category
            need_save = True

        # condition
        condition = kwargs.get('condition', None)
        if condition is not None and condition != o.condition:
            o.condition = condition
            need_save = True

        # product_key
        product_key = kwargs.get('product_key', None)
        if product_key is not None and product_key != o.product_key:
            o.product_key = product_key
            need_save = True

        # article
        article = kwargs.get('article', None)
        if article is not None and article != o.article:
            o.article = article
            need_save = True

        # name_rus
        name_rus = kwargs.get('name_rus', None)
        if name_rus is not None and name_rus != o.name_rus:
            o.name_rus = name_rus
            need_save = True

        # name_other
        name_other = kwargs.get('name_other', None)
        if name_other is not None and name_other != o.name_other:
            o.name_other = name_other
            need_save = True

        # description
        description = kwargs.get('description', None)
        if description is not None and description != o.description:
            o.description = description
            need_save = True

        # ean_128
        ean_128 = kwargs.get('ean_128', None)
        if ean_128 is not None and ean_128 != o.ean_128:
            o.ean_128 = ean_128
            need_save = True

        # upc
        upc = kwargs.get('upc', None)
        if upc is not None and upc != o.upc:
            o.upc = upc
            need_save = True

        # pnc
        pnc = kwargs.get('pnc', None)
        if pnc is not None and pnc != o.pnc:
            o.pnc = pnc
            need_save = True

        # hs_code
        hs_code = kwargs.get('hs_code', None)
        if hs_code is not None and hs_code != o.hs_code:
            o.hs_code = hs_code
            need_save = True

        # traceable
        traceable = kwargs.get('traceable', None)
        if traceable is not None and traceable != o.traceable:
            o.traceable = traceable
            need_save = True

        # condition_description
        condition_description = kwargs.get('condition_description', None)
        if condition_description is not None and condition_description != o.condition_description:
            o.condition_description = condition_description
            need_save = True

        # weight
        weight = kwargs.get('weight', None)
        if weight is not None and weight != o.weight:
            o.weight = weight
            need_save = True

        # width
        width = kwargs.get('width', None)
        if width is not None and width != o.width:
            o.width = width
            need_save = True

        # height
        height = kwargs.get('height', None)
        if height is not None and height != o.height:
            o.height = height
            need_save = True

        # depth
        depth = kwargs.get('depth', None)
        if depth is not None and depth != o.depth:
            o.depth = depth
            need_save = True

        # volume
        volume = kwargs.get('volume', None)
        if volume is not None and volume != o.volume:
            o.volume = volume
            need_save = True

        # multiplicity
        multiplicity = kwargs.get('multiplicity', None)
        if multiplicity is not None and multiplicity != o.multiplicity:
            o.multiplicity = multiplicity
            need_save = True

        # unit
        unit = kwargs.get('unit', None)
        if unit is not None and unit != o.unit:
            o.unit = unit
            need_save = True

        if need_save:
            o.save()

        return o

    def take_by_article(self, distributor, vendor, article, **kwargs):
        pass


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_key = models.TextField(null=True, default=None, db_index=True)
    party_key = models.TextField(null=True, default=None, db_index=True)
    article = models.TextField(null=True, default=None, db_index=True)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    vendor = models.ForeignKey('Vendor', null=True, default=None,
                               on_delete=models.CASCADE, related_name='+')
    category = models.ForeignKey('Category', null=True, default=None,
                                 on_delete=models.CASCADE, related_name='+')
    name = models.TextField(null=True, default=None, db_index=True)
    short_name = models.TextField(null=True, default=None, db_index=True)
    name_rus = models.TextField(null=True, default=None, db_index=True)
    name_other = models.TextField(null=True, default=None, db_index=True)
    description = models.TextField(null=True, default=None)

    # Коды
    ean_128 = models.TextField(null=True, default=None, db_index=True)
    upc = models.TextField(null=True, default=None, db_index=True)
    pnc = models.TextField(null=True, default=None, db_index=True)
    hs_code = models.TextField(null=True, default=None, db_index=True)

    # Прослеживаемый товар
    traceable = models.BooleanField(null=True, default=None, db_index=True)

    # Кондиционность
    condition = models.ForeignKey('Condition', null=True, default=None,
                                  on_delete=models.CASCADE, related_name='+')
    condition_description = models.TextField(null=True, default=None)

    # Характеристики упаковки
    weight = models.DecimalField(max_digits=18, decimal_places=9, null=True, default=None)
    width = models.DecimalField(max_digits=18, decimal_places=9, null=True, default=None)
    height = models.DecimalField(max_digits=18, decimal_places=9, null=True, default=None)
    depth = models.DecimalField(max_digits=18, decimal_places=9, null=True, default=None)
    volume = models.DecimalField(max_digits=18, decimal_places=9, null=True, default=None)
    multiplicity = models.IntegerField(null=True, default=None)
    unit = models.ForeignKey('Unit', null=True, default=None,
                             on_delete=models.CASCADE, related_name='+')

    # Контент
    content = models.TextField(null=True, default=None)
    content_loaded = models.DateTimeField(null=True, default=None)

    objects = ProductManager()

    def __str__(self):
        return f'{self.vendor.name} [{self.article}]'

    class Meta:
        ordering = ['vendor__name', 'article']


class CurrencyManager(models.Manager):

    def take(self, key, **kwargs):
        if not key:
            return None

        try:
            o = self.get(key=key)

        except Currency.DoesNotExist:
            o = Currency()
            o.key = key[:32]
            o.save()

        if o.name is None:
            o.name = key
            o.save()

        return o


class Currency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=32, unique=True)

    name = models.TextField(null=True, default=None, db_index=True)
    print_name = models.TextField(null=True, default=None, db_index=True)

    objects = CurrencyManager()

    def __str__(self):
        return f'{self.key}'

    class Meta:
        ordering = ['key']


class LocationManager(models.Manager):

    def take(self, key, **kwargs):
        if not key:
            return None

        need_save = False

        try:
            o = self.get(key=key)

        except Location.DoesNotExist:
            o = Location()
            o.key = key[:128]
            need_save = True

        if o.name is None:
            o.name = key
            need_save = True

        description = kwargs.get('description', None)
        if description is not None and o.description is None:
            o.description = description
            need_save = True

        if need_save:
            o.save()

        return o


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=128, unique=True)

    name = models.TextField(null=True, default=None, db_index=True)
    description = models.TextField(null=True, default=None)

    objects = LocationManager()

    def __str__(self):
        return f'{self.key}'

    class Meta:
        ordering = ['name']


class PartyManager(models.Manager):

    pass


class Party(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    product = models.ForeignKey('Product', null=True, default=None,
                                on_delete=models.CASCADE, related_name='+')

    # Цены
    price_in = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    currency_in = models.ForeignKey('Currency', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    price_out = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    currency_out = models.ForeignKey('Currency', null=True, default=None,
                                     on_delete=models.CASCADE, related_name='+')
    price_out_open = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    currency_out_open = models.ForeignKey('Currency', null=True, default=None,
                                          on_delete=models.CASCADE, related_name='+')
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
        return f'{self.product} | {self.quantity} = {self.price_in} {self.currency_in}'

    class Meta:
        ordering = ['created']


class ParameterGroupManager(models.Manager):

    def take(self, name, **kwargs):
        if not name:
            return None

        try:
            o = self.get(name=name)

        except ParameterGroup.DoesNotExist:
            o = ParameterGroup()
            o.name = name
            o.save()

        return o


class ParameterGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    name = models.TextField(null=True, default=None, db_index=True)

    objects = ParameterGroupManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['name']


class ParameterManager(models.Manager):

    def take(self, distributor, name, **kwargs):
        if not distributor or not name:
            return None

        need_save = False

        try:
            o = self.get(distributor=distributor, name=name)

        except Parameter.DoesNotExist:
            o = Parameter()
            o.name = name
            need_save = True

        group = kwargs.get('group', None)
        if group is not None and o.group is None:
            o.group = group
            need_save = True

        description = kwargs.get('description', None)
        if description is not None and o.description is None:
            o.description = description
            need_save = True

        if need_save:
            o.save()

        return o


class Parameter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    group = models.ForeignKey('ParameterGroup', null=True, default=None,
                              on_delete=models.CASCADE, related_name='+')
    name = models.TextField(null=True, default=None, db_index=True)
    description = models.TextField(null=True, default=None)

    objects = ParameterManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['name']


class ParameterUnitManager(models.Manager):

    def take(self, key, **kwargs):
        if not key:
            return None

        need_save = False

        try:
            o = self.get(key=key)

        except ParameterUnit.DoesNotExist:
            o = ParameterUnit()
            o.key = key[:32]
            need_save = True

        if o.name is None:
            o.name = key
            need_save = True

        if need_save:
            o.save()

        return o


class ParameterUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=32, unique=True)

    name = models.TextField(null=True, default=None, db_index=True)
    print_name = models.TextField(null=True, default=None, db_index=True)

    objects = ParameterUnitManager()

    def __str__(self):
        return f'{self.key}'

    class Meta:
        ordering = ['key']


class ParameterValueManager(models.Manager):

    def take(self, distributor, product, parameter, **kwargs):
        if not distributor or not product or not parameter:
            return None

        need_save = False

        try:
            o = self.get(distributor=distributor, product=product, parameter=parameter)

        except ParameterValue.DoesNotExist:
            o = ParameterValue()
            o.distributor = distributor
            o.product = product
            o.parameter = parameter
            need_save = True

        value = kwargs.get('value', None)
        if value and value != o.value:
            o.value = value
            need_save = True

        unit = kwargs.get('unit', None)
        if unit and unit != o.unit:
            o.unit = unit
            need_save = True

        if need_save:
            o.save()

        return o


class ParameterValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    product = models.ForeignKey('Product', null=True, default=None,
                                on_delete=models.CASCADE, related_name='+')
    parameter = models.ForeignKey('Parameter', null=True, default=None,
                                  on_delete=models.CASCADE, related_name='+')

    value = models.TextField(null=True, default=None, db_index=True)
    unit = models.ForeignKey('ParameterUnit', null=True, default=None,
                             on_delete=models.CASCADE, related_name='+')

    objects = ParameterValueManager()

    def __str__(self):
        if self.unit:
            return f'{self.product}: {self.parameter} = {self.value} {self.unit}'
        else:
            return f'{self.product}: {self.parameter} = {self.value}'


class ProductImageManager(models.Manager):

    def take(self, product, source_url, **kwargs):
        if not product or not source_url:
            return None

        try:
            o = self.get(product=product, source_url=source_url)

        except ProductImage.DoesNotExist:
            o = ProductImage()
            o.product = product
            o.source_url = source_url
            o.save()

        if o.file_name is None:
            o.download_file()

        return o


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('Product', null=True, default=None,
                                on_delete=models.CASCADE, related_name='+')
    source_url = models.TextField(null=True, default=None, db_index=True)
    file_name = models.TextField(null=True, default=None)

    objects = ProductImageManager()

    def download_file(self):

        # Определяем имя файла
        ext = self.source_url.rpartition('.')
        self.file_name = f'{settings.MEDIA_ROOT}distributors/products/photos/{self.id}.{ext[2]}'

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
