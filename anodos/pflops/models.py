import os
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.indexes import GinIndex

import anodos.fixers


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
        self.slug = anodos.fixers.to_slug(name=self.name)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']


class UnitManager(models.Manager):

    def take(self, name, **kwargs):
        if not name:
            return None

        name = anodos.fixers.fix_text(name)

        need_save = False

        try:
            o = self.get(name=name)

        except Unit.DoesNotExist:
            o = Unit()
            o.name = name
            need_save = True

        if need_save:
            o.save()

        return o


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

    def take(self, key, **kwargs):
        if key is None:
            return None

        key = anodos.fixers.fix_text(key)

        need_save = False

        try:
            o = self.get(key__iexact=key)

        except Currency.DoesNotExist:
            o = Currency()
            o.key = key
            need_save = True

        # key_digit
        key_digit = kwargs.get('key_digit', None)
        key_digit = anodos.fixers.fix_text(key_digit)
        if key_digit is not None and o.key_digit is None:
            o.key_digit = key_digit
            need_save = True

        # name
        name = kwargs.get('name', None)
        name = anodos.fixers.fix_text(name)
        if name is not None and o.name is None:
            o.name = name
            need_save = True

        # quantity
        quantity = kwargs.get('quantity', None)
        quantity = anodos.fixers.fix_float(quantity)
        if quantity is not None and o.quantity != quantity:
            o.quantity = quantity
            need_save = True

        # rate
        rate = kwargs.get('rate', None)
        rate = anodos.fixers.fix_float(rate)
        if rate is not None and o.rate != rate:
            o.rate = rate
            need_save = True

        if need_save:
            o.save()

        return o


class Currency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=32, unique=True)
    key_digit = models.CharField(max_length=32, null=True, default=None, unique=True)

    name = models.TextField(null=True, default=None, db_index=True)
    full_name = models.TextField(null=True, default=None, db_index=True)

    quantity = models.FloatField(null=True, default=None)
    rate = models.FloatField(null=True, default=None)

    objects = CurrencyManager()

    def __str__(self):
        return f'{self.key} = {self.rate} / {self.quantity}'

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

    def take(self, vendor, part_number, **kwargs):

        if not vendor or not part_number:
            return None

        need_save = False

        try:
            o = self.get(vendor=vendor, part_number=part_number)
        except Product.DoesNotExist:
            o = Product()
            o.vendor = vendor
            o.part_number = part_number
            need_save = True

        # category
        category = kwargs.get('category', None)
        if category is not None and o.category is None:
            o.category = category
            need_save = True

        # name
        name = kwargs.get('name', None)
        name = anodos.fixers.fix_text(name)
        if name is not None and o.name is None:
            o.name = name
            need_save = True

        # short_name
        short_name = kwargs.get('short_name', None)
        short_name = anodos.fixers.fix_text(short_name)
        if short_name is not None and o.short_name is None:
            o.short_name = short_name
            need_save = True

        # name_rus
        name_rus = kwargs.get('name_rus', None)
        name_rus = anodos.fixers.fix_text(name_rus)
        if name_rus is not None and o.name_rus is None:
            o.name_rus = name_rus
            need_save = True

        # name_other
        name_other = kwargs.get('name_other', None)
        name_other = anodos.fixers.fix_text(name_other)
        if name_other is not None and o.name_other is None:
            o.name_other = name_other
            need_save = True

        # description
        description = kwargs.get('description', None)
        description = anodos.fixers.fix_text(description)
        if description is not None and o.description is None:
            o.description = description
            need_save = True

        # warranty
        warranty = kwargs.get('warranty', None)
        warranty = anodos.fixers.fix_text(warranty)
        if warranty is not None and o.warranty is None:
            o.warranty = warranty
            need_save = True

        # ean_128
        ean_128 = kwargs.get('ean_128', None)
        if ean_128 is not None and o.ean_128 is None:
            o.ean_128 = ean_128
            need_save = True

        # upc
        upc = kwargs.get('upc', None)
        if upc is not None and o.upc is None:
            o.upc = upc
            need_save = True

        # pnc
        pnc = kwargs.get('pnc', None)
        if pnc is not None and o.pnc is None:
            o.pnc = pnc
            need_save = True

        # hs_code
        hs_code = kwargs.get('hs_code', None)
        if hs_code is not None and o.hs_code is None:
            o.hs_code = hs_code
            need_save = True

        # gtin
        gtin = kwargs.get('gtin', None)
        if gtin is not None and o.gtin is None:
            o.gtin = gtin
            need_save = True

        # tnved
        tnved = kwargs.get('tnved', None)
        if tnved is not None and o.tnved is None:
            o.tnved = tnved
            need_save = True

        # traceable
        traceable = kwargs.get('traceable', None)
        if traceable is not None and o.traceable is None:
            o.traceable = traceable
            need_save = True

        # unconditional
        unconditional = kwargs.get('unconditional', None)
        if unconditional is not None and o.unconditional is None:
            o.unconditional = unconditional
            need_save = True

        # sale
        sale = kwargs.get('sale', None)
        if sale is not None and o.sale is None:
            o.sale = sale
            need_save = True

        # promo
        promo = kwargs.get('promo', None)
        if promo is not None and o.promo is None:
            o.promo = promo
            need_save = True

        # outoftrade
        outoftrade = kwargs.get('outoftrade', None)
        if outoftrade is not None and o.outoftrade is None:
            o.outoftrade = outoftrade
            need_save = True

        # condition_description
        condition_description = kwargs.get('condition_description', None)
        if condition_description is not None and o.condition_description is None:
            o.condition_description = condition_description
            need_save = True

        # weight
        weight = kwargs.get('weight', None)
        if weight is not None and o.weight is None:
            o.weight = weight
            need_save = True

        # width
        width = kwargs.get('width', None)
        if width is not None and o.width is None:
            o.width = width
            need_save = True

        # height
        height = kwargs.get('height', None)
        if height is not None and o.height is None:
            o.height = height
            need_save = True

        # depth
        depth = kwargs.get('depth', None)
        if depth is not None and o.depth is None:
            o.depth = depth
            need_save = True

        # volume
        volume = kwargs.get('volume', None)
        if volume is not None and o.volume is None:
            o.volume = volume
            need_save = True

        # multiplicity
        multiplicity = kwargs.get('multiplicity', None)
        if multiplicity is not None and o.multiplicity is None:
            o.multiplicity = multiplicity
            need_save = True

        # unit
        unit = kwargs.get('unit', None)
        if unit is not None and o.unit is None:
            o.unit = unit
            need_save = True

        # content
        content = kwargs.get('content', None)
        if content is not None and o.content is None:
            o.content = content
            need_save = True

        if need_save:
            o.save()

        return o


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    part_number = models.TextField(null=True, default=None, db_index=True)
    vendor = models.ForeignKey('Vendor', null=True, default=None,
                               on_delete=models.CASCADE, related_name='+')
    category = models.ForeignKey('Category', null=True, default=None,
                                 on_delete=models.SET_NULL, related_name='+')
    names_search = models.TextField(null=True, default=None, db_index=True)
    parameters_search = models.TextField(null=True, default=None, db_index=True)
    slug = models.TextField(db_index=True, null=True, default=None)

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
    images_loaded = models.DateTimeField(null=True, default=None)

    # Служебное
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(null=True, default=None)
    edited = models.DateTimeField(null=True, default=None)

    objects = ProductManager()

    def __str__(self):
        if self.vendor is None:
            return f'None [{self.part_number}] ({self.id}) {self.slug}'
        else:
            return f'{self.vendor.name} [{self.part_number}] ({self.id}) {self.slug}'

    def save(self, *args, **kwargs):
        if self.vendor:
            self.names_search = f'{self.name.lower()} ' \
                          f'{self.part_number.lower()} ' \
                          f'{self.vendor.name.lower()}'
            self.slug = anodos.fixers.to_slug(f'{self.vendor.name} {self.part_number}')
        else:
            self.names_search = f'{self.name.lower()} ' \
                          f'{self.part_number.lower()}'
            self.slug = anodos.fixers.to_slug(f'{self.part_number}')
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created']
        indexes = [GinIndex(fields=['names_search', 'parameters_search'],
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

    def take(self, product, parameter, **kwargs):
        if not product or not parameter:
            return None

        need_save = False

        try:
            o = self.get(product=product, parameter=parameter)

        except ParameterValue.DoesNotExist:
            o = ParameterValue()
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
    product = models.ForeignKey('Product', null=True, default=None,
                                on_delete=models.CASCADE, related_name='+')
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

    def take(self, product, source_url, **kwargs):
        if not product or not source_url:
            return None

        source_url = anodos.fixers.fix_text(source_url)

        need_save = False

        try:
            o = self.get(product=product, source_url=source_url)

        except ProductImage.DoesNotExist:
            o = ProductImage()
            o.product = product
            o.source_url = source_url
            need_save = True

        if need_save:
            o.save()

        return o


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('Product', null=True, default=None,
                                on_delete=models.CASCADE, related_name='+')
    source_url = models.TextField(null=True, default=None, db_index=True)
    file_name = models.TextField(null=True, default=None)

    created = models.DateTimeField(default=timezone.now, db_index=True)

    objects = ProductImageManager()

    def create_directory_for_file(self):
        directory = '/'
        for dir_ in self.file_name.split('/')[:-1]:
            directory = '{}/{}'.format(directory, dir_)
            if not os.path.exists(directory):
                os.makedirs(directory)

    def delete(self, *args, **kwargs):
        try:
            os.remove(self.file_name)
        except FileNotFoundError:
            pass
        except TypeError:
            pass
        super().delete(*args, **kwargs)

    @property
    def url(self):
        if self.file_name:
            return self.file_name.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
        else:
            return None

    def __str__(self):
        if self.file_name:
            return f'{self.product}: {self.url}'
        else:
            return f'{self.product}: {self.source_url}'

    class Meta:
        ordering = ['created']
