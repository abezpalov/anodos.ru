import io
import os
import uuid
import requests as r
import PIL

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.indexes import GinIndex

import anodos.tools


class DistributorManager(models.Manager):

    def take(self, name, **kwargs):
        if not name:
            return None

        need_save = False

        try:
            o = self.get(name=name)

        except Distributor.DoesNotExist:
            o = Distributor()
            o.name = name[:512]
            need_save = True

        if need_save:
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

    def take(self, distributor, key=None, name=None, parent=None):
        if not distributor:
            return None
        if not key and not name:
            return None

        need_save = False

        if key:
            try:
                o = self.get(distributor=distributor, key=key)
            except Category.DoesNotExist:
                o = Category()
                o.distributor = distributor
                o.key = key
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
                o.name = o.key
                need_save = True

        else:
            print('Category.take not work on name')
            return None

        if need_save:
            o.save()

        return o

    def get_by_key(self, distributor, key):
        try:
            o = self.get(distributor=distributor, name__contains=f'[{key}]')
        except Category.DoesNotExist:
            return None
        return o


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    to_pflops = models.ForeignKey('pflops.Category', null=True, default=None,
                                  on_delete=models.SET_NULL, related_name='+')
    key = models.TextField(db_index=True, null=True, default=None)
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

        need_save = False

        try:
            o = self.get(distributor=distributor, name__iexact=name)

        except Vendor.DoesNotExist:
            o = Vendor()
            o.distributor = distributor
            o.name = name
            need_save = True

        if need_save:
            o.save()

        return o


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    to_pflops = models.ForeignKey('pflops.Vendor', null=True, default=None,
                                  on_delete=models.SET_NULL, related_name='+')
    name = models.TextField(db_index=True)

    objects = VendorManager()

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
    to_pflops = models.ForeignKey('pflops.Unit', null=True, default=None,
                                  on_delete=models.SET_NULL, related_name='+')

    name = models.TextField(null=True, default=None, db_index=True)

    objects = UnitManager()

    def __str__(self):
        return f'{self.key}'

    class Meta:
        ordering = ['key']


class CurrencyManager(models.Manager):

    def take(self, key, **kwargs):

        if key is None:
            return None

        if key == "RUR":
            key = "RUB"

        key = anodos.tools.fix_text(key)

        need_save = False

        try:
            o = self.get(key__iexact=key)

        except Currency.DoesNotExist:
            o = Currency()
            o.key = key
            need_save = True

        # key_digit
        key_digit = kwargs.get('key_digit', None)
        key_digit = anodos.tools.fix_text(key_digit)
        if key_digit is not None and o.key_digit is None:
            o.key_digit = key_digit
            need_save = True

        # name
        name = kwargs.get('name', None)
        name = anodos.tools.fix_text(name)
        if name is not None and o.name is None:
            o.name = name
            need_save = True

        # quantity
        quantity = kwargs.get('quantity', None)
        quantity = anodos.tools.fix_float(quantity)
        if quantity is not None and o.quantity != quantity:
            o.quantity = quantity
            need_save = True

        # rate
        rate = kwargs.get('rate', None)
        rate = anodos.tools.fix_float(rate)
        if rate is not None and o.rate != rate:
            o.rate = rate
            need_save = True

        if need_save:
            o.save()

        return o


class Currency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=32, unique=True)
    key_digit = models.CharField(max_length=32, null=True, default=None)

    name = models.TextField(null=True, default=None, db_index=True)
    full_name = models.TextField(null=True, default=None, db_index=True)

    quantity = models.FloatField(default=1.0)
    rate = models.FloatField(default=1.0)

    objects = CurrencyManager()

    def __str__(self):
        return f'{self.key}'

    class Meta:
        ordering = ['key']


class PriceManager(models.Manager):

    pass


class Price(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.ForeignKey('Currency', null=True, on_delete=models.CASCADE, related_name='+')

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

    def take_by_party_key(self, distributor, party_key, name, **kwargs):

        if not distributor or not party_key or not name:
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

        # product_key
        product_key = kwargs.get('product_key', None)
        if product_key is not None and product_key != o.product_key:
            o.product_key = product_key
            need_save = True

        # part_number
        part_number = kwargs.get('part_number', None)
        if part_number is not None and part_number != o.part_number:
            o.part_number = part_number
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

        # name
        if name is not None and name != o.name:
            o.name = name
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

        # warranty
        warranty = kwargs.get('warranty', None)
        if warranty is not None and warranty != o.warranty:
            o.warranty = warranty
            need_save = True

        # url
        url = kwargs.get('url', None)
        if url is not None and url != o.url:
            o.url = url
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

        # gtin
        gtin = kwargs.get('gtin', None)
        if gtin is not None and gtin != o.gtin:
            o.gtin = gtin
            need_save = True

        # tnved
        tnved = kwargs.get('tnved', None)
        if tnved is not None and tnved != o.tnved:
            o.tnved = tnved
            need_save = True

        # traceable
        traceable = kwargs.get('traceable', None)
        if traceable is not None and traceable != o.traceable:
            o.traceable = traceable
            need_save = True

        # weight
        weight = kwargs.get('weight', None)
        if weight is not None and weight != o.weight:
            o.weight = weight
            need_save = True

        # width
        width = kwargs.get('width', None)
        if anodos.tools.need_new_decimal_value(old=o.width, new=width):
            o.width = width
            need_save = True

        # height
        height = kwargs.get('height', None)
        if anodos.tools.need_new_decimal_value(old=o.height, new=height):
            o.height = height
            need_save = True

        # depth
        depth = kwargs.get('depth', None)
        if anodos.tools.need_new_decimal_value(old=o.depth, new=depth):
            o.depth = depth
            need_save = True

        # volume
        volume = kwargs.get('volume', None)
        if anodos.tools.need_new_decimal_value(old=o.volume, new=volume):
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

    def take_by_part_number(self, distributor, vendor, part_number, name, **kwargs):

        if not distributor or not vendor or not part_number or not name:
            return None

        need_save = False

        try:
            o = self.get(distributor=distributor, vendor=vendor, part_number=part_number)
        except Product.DoesNotExist:
            o = Product()
            o.distributor = distributor
            o.vendor = vendor
            o.part_number = part_number
            o.name = name
            need_save = True

        # party_key
        party_key = kwargs.get('party_key', None)
        if party_key is not None and party_key != o.party_key:
            o.party_key = party_key
            need_save = True

        # product_key
        product_key = kwargs.get('product_key', None)
        if product_key is not None and product_key != o.product_key:
            o.product_key = product_key
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

        # name
        if name is not None and name != o.name:
            o.name = name
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

        # warranty
        warranty = kwargs.get('warranty', None)
        if warranty is not None and warranty != o.warranty:
            o.warranty = warranty
            need_save = True

        # url
        url = kwargs.get('url', None)
        if url is not None and url != o.url:
            o.url = url
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

        # gtin
        gtin = kwargs.get('gtin', None)
        if gtin is not None and gtin != o.gtin:
            o.gtin = gtin
            need_save = True

        # tnved
        tnved = kwargs.get('tnved', None)
        if tnved is not None and tnved != o.tnved:
            o.tnved = tnved
            need_save = True

        # traceable
        traceable = kwargs.get('traceable', None)
        if traceable is not None and traceable != o.traceable:
            o.traceable = traceable
            need_save = True

        # weight
        weight = kwargs.get('weight', None)
        if weight is not None and weight != o.weight:
            o.weight = weight
            need_save = True

        # width
        width = kwargs.get('width', None)
        if anodos.tools.need_new_decimal_value(old=o.width, new=width):
            o.width = width
            need_save = True

        # height
        height = kwargs.get('height', None)
        if anodos.tools.need_new_decimal_value(old=o.height, new=height):
            o.height = height
            need_save = True

        # depth
        depth = kwargs.get('depth', None)
        if anodos.tools.need_new_decimal_value(old=o.depth, new=depth):
            o.depth = depth
            need_save = True

        # volume
        volume = kwargs.get('volume', None)
        if anodos.tools.need_new_decimal_value(old=o.volume, new=volume):
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


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_key = models.TextField(null=True, default=None, db_index=True)
    party_key = models.TextField(null=True, default=None, db_index=True)
    part_number = models.TextField(null=True, default=None, db_index=True)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    vendor = models.ForeignKey('Vendor', null=True, default=None,
                               on_delete=models.CASCADE, related_name='+')
    category = models.ForeignKey('Category', null=True, default=None,
                                 on_delete=models.CASCADE, related_name='+')

    to_pflops = models.ForeignKey('pflops.Product', null=True, default=None,
                                  on_delete=models.SET_NULL, related_name='+')

    name = models.TextField(null=True, default=None, db_index=True)
    short_name = models.TextField(null=True, default=None, db_index=True)
    name_rus = models.TextField(null=True, default=None, db_index=True)
    name_other = models.TextField(null=True, default=None, db_index=True)
    description = models.TextField(null=True, default=None)
    warranty = models.TextField(null=True, default=None)

    # Ссылка на первоисточник информации
    url = models.TextField(null=True, default=None, db_index=True)

    # Коды
    ean_128 = models.TextField(null=True, default=None, db_index=True)
    upc = models.TextField(null=True, default=None, db_index=True)
    pnc = models.TextField(null=True, default=None, db_index=True)
    hs_code = models.TextField(null=True, default=None, db_index=True)
    gtin = models.TextField(null=True, default=None, db_index=True)
    tnved = models.TextField(null=True, default=None, db_index=True)

    # Прослеживаемый товар
    traceable = models.BooleanField(null=True, default=None, db_index=True)

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

    created = models.DateTimeField(default=timezone.now)

    objects = ProductManager()

    @property
    def price(self):
        parties = Party.objects.filter(product=self)
        for party in parties:
            if party.quantity and party.price:
                return party.price
        for party in parties:
            if party.price:
                return party.price
        return None

    @property
    def quantity(self):
        quantity = 0
        parties = Party.objects.filter(product=self)
        for party in parties:
            if party.quantity:
                quantity += party.quantity
        return quantity

    def __str__(self):
        if self.vendor is None:
            return f'None [{self.part_number}] ({self.id})'
        else:
            return f'{self.vendor.name} [{self.part_number}] ({self.id})'

    class Meta:
        ordering = ['vendor__name', 'part_number']


class LocationManager(models.Manager):

    def take(self, distributor, key, **kwargs):
        if not distributor or not key:
            return None

        need_save = False

        try:
            o = self.get(distributor=distributor, key=key)

        except Location.DoesNotExist:
            o = Location()
            o.distributor = distributor
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
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    key = models.CharField(max_length=128, unique=True)

    name = models.TextField(null=True, default=None, db_index=True)
    description = models.TextField(null=True, default=None)

    objects = LocationManager()

    def __str__(self):
        return f'{self.key}'

    class Meta:
        ordering = ['name']


class PartyManager(models.Manager):

    def create(self, product=None, distributor=None, **kwargs):

        if product is None or distributor is None:
            return None

        # price_in
        price_in = kwargs.get('price_in', None)
        currency_in = kwargs.get('currency_in', None)
        if price_in and currency_in:
            price_in = Price.objects.create(value=price_in, currency=currency_in)
        else:
            price_in = None

        # price_out
        price_out = kwargs.get('price_out', None)
        currency_out = kwargs.get('currency_out', None)
        if price_out and currency_out:
            price_out = Price.objects.create(value=price_out, currency=currency_out)
        else:
            price_out = None

        # price_out_open
        price_out_open = kwargs.get('price_out_open', None)
        currency_out_open = kwargs.get('currency_out_open', None)
        if price_out_open and currency_out_open:
            price_out_open = Price.objects.create(value=price_out_open, currency=currency_out_open)
        else:
            price_out_open = None

        # price
        if price_out_open:
            price = Price.objects.create(value=price_out_open.value,
                                         currency=price_out_open.currency)
        elif price_out:
            price = Price.objects.create(value=price_out.value,
                                         currency=price_out.currency)
        elif price_in:
            price = Price.objects.create(value=price_in.value*settings.MARGIN,
                                         currency=price_in.currency)
        else:
            price = None

        # TODO сделать перевод в рубли

        must_keep_end_user_price = kwargs.get('must_keep_end_user_price', None)
        location = kwargs.get('location', None)
        quantity = kwargs.get('quantity', None)
        quantity_great_than = kwargs.get('quantity_great_than', None)
        unit = kwargs.get('unit', None)
        can_reserve = kwargs.get('can_reserve', None)
        is_available_for_order = kwargs.get('is_available_for_order', None)

        # Кондиционность и распродажа
        unconditional = kwargs.get('unconditional', False)
        sale = kwargs.get('sale', False)
        promo = kwargs.get('promo', False)
        outoftrade = kwargs.get('outoftrade', False)
        condition_description = kwargs.get('condition_description', None)

        o = super().create(distributor=distributor,
                           product=product,
                           price=price,
                           price_in=price_in,
                           price_out=price_out,
                           price_out_open=price_out_open,
                           must_keep_end_user_price=must_keep_end_user_price,
                           location=location,
                           quantity=quantity,
                           quantity_great_than=quantity_great_than,
                           unit=unit,
                           can_reserve=can_reserve,
                           is_available_for_order=is_available_for_order,
                           unconditional=unconditional,
                           sale=sale,
                           promo=promo,
                           outoftrade=outoftrade,
                           condition_description=condition_description)
        return o


class Party(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
    product = models.ForeignKey('Product', null=True, default=None,
                                on_delete=models.CASCADE, related_name='+')
    search = models.TextField(null=True, default=None, db_index=True)

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

    # Кондиционность и распродажа
    unconditional = models.BooleanField(default=False, db_index=True)
    sale = models.BooleanField(default=False, db_index=True)
    promo = models.BooleanField(default=False, db_index=True)
    outoftrade = models.BooleanField(default=False, db_index=True)
    condition_description = models.TextField(null=True, default=None)

    created = models.DateTimeField(default=timezone.now)

    objects = PartyManager()

    def __str__(self):
        return f'{self.product} | {self.quantity} on {self.location}'

    def save(self, *args, **kwargs):
        if self.product.vendor:
            self.search = f'{self.product.name.lower()} ' \
                          f'{self.product.part_number.lower()} ' \
                          f'{self.product.vendor.name.lower()}'
        else:
            self.search = f'{self.product.name.lower()} ' \
                          f'{self.product.part_number.lower()}'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created']
        indexes = [GinIndex(fields=['search'],
                            name='party_search_idx',
                            )]


class ParameterManager(models.Manager):

    def take(self, distributor, name, **kwargs):
        if not distributor or not name:
            return None

        need_save = False

        name = anodos.tools.fix_text(name)

        try:
            o = self.get(distributor=distributor, name__iexact=name)

        except Parameter.DoesNotExist:
            o = Parameter()
            o.name = name
            o.distributor = distributor
            need_save = True

        except Parameter.MultipleObjectsReturned:
            os_ = self.filter(distributor=distributor, name=name)
            for n, o_ in enumerate(os_):
                if n == 0:
                    o = o_
                else:
                    o_.delete()

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

    to_pflops = models.ForeignKey('pflops.Parameter', null=True, default=None,
                                  on_delete=models.SET_NULL, related_name='+')

    name = models.TextField(null=True, default=None, db_index=True)
    description = models.TextField(null=True, default=None)

    objects = ParameterManager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['name']
        unique_together = ['distributor', 'name']


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

    to_pflops = models.ForeignKey('pflops.Unit', null=True, default=None,
                                  on_delete=models.SET_NULL, related_name='+')

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

        need_save = False

        try:
            o = self.get(product=product, source_url=source_url)

        except ProductImage.DoesNotExist:
            o = ProductImage()
            o.product = product
            o.source_url = source_url
            need_save = True

        except ProductImage.MultipleObjectsReturned:
            imgs = self.filter(product=product, source_url=source_url)
            o = imgs[0]
            for n, img in enumerate(imgs):
                if n > 0:
                    if img.file_name:
                        os.remove(img.file_name)
                    img.delete()

        ext = kwargs.get('ext', None)
        if ext and ext != o.ext:
            o.ext = ext
            need_save = True

        if need_save:
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

    created = models.DateTimeField(default=timezone.now, db_index=True)

    objects = ProductImageManager()

    @property
    def url(self):
        if self.file_name:
            return self.file_name.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
        else:
            return None

    def download_file(self):

        # Загружаем фотографию
        result = r.get(self.source_url)

        # Проверяем на целостность
        try:
            im = PIL.Image.open(io.BytesIO(result.content))
        except PIL.UnidentifiedImageError:
            print(f'Ошибка! не удалось прочитать изображение {self.source_url}.')
            return None

        # Сохраняем в PNG
        self.file_name = f'{settings.MEDIA_ROOT}distributors/products/photos/{self.id}.png'
        self.create_directory_for_file()
        im.save(self.file_name, "PNG")
        im.save()
        self.save()

        # Закрываем файл
        im.close()

    def create_directory_for_file(self):
        directory = '/'
        for dir_ in self.file_name.split('/')[:-1]:
            directory = '{}/{}'.format(directory, dir_)
            if not os.path.exists(directory):
                os.makedirs(directory)
        return True

    def __str__(self):
        return f'{self.product}: {self.source_url}'

    class Meta:
        ordering = ['created']
