import os
import io
import PIL
import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.indexes import GinIndex

import anodos.tools


class ImageManager(models.Manager):

    def upload(self, bytes, style='catalog'):

        if style == 'catalog':
            width = 400
            height = 240
        else:
            width = 400
            height = 240

        im = PIL.Image.open(io.BytesIO(bytes))

        # Масштабируем исходное изображение
        dx = width / im.size[0]
        dy = height / im.size[1]
        d = max(dx, dy)
        im = im.resize((int(im.size[0]*d), int(im.size[1]*d)))

        # Создаём новое изображение и вставляем в него участок исходного
        im_new = PIL.Image.new('RGBA', (width, height), '#00000000')
        dx = (width - im.size[0]) // 2
        dy = (height - im.size[1]) // 2
        im_new.paste(im, (dx, dy))

        # Закрываем исходное изображение
        im.close()

        # Создаём объект изображения в базе
        image = self.create()
        image.file_name = f'{settings.MEDIA_ROOT}catalog/photos/{image.id}.png'
        image.create_directory_for_file()
        image.save()

        im_new.save(image.file_name, "PNG")
        im_new.close()

        return image


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.TextField(null=True, default=None)

    created = models.DateTimeField(default=timezone.now, db_index=True)

    objects = ImageManager()

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
        return f'{self.url}'

    class Meta:
        ordering = ['-created']


class CatalogElementManager(models.Manager):

    def create(self, title=None, slug=None, parent=None, image=None):

        if title is None:
            return None

        if slug:
            slug = anodos.tools.to_slug(slug)
        else:
            slug = anodos.tools.to_slug(title)

        try:
            image = Image.objects.get(id=image)
        except Image.DoesNotExist:
            return None

        try:
            parent = self.get(id=parent)
        except CatalogElement.DoesNotExist:
            parent = None

        o = super().create(parent=parent, title=title, slug=slug, image=image)

        return o


class CatalogElement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey('CatalogElement', null=True, default=None,
                               on_delete=models.SET_NULL, related_name='+')
    image = models.ForeignKey('Image', null=True, default=None,
                              on_delete=models.SET_NULL, related_name='+')
    title = models.TextField(db_index=True)
    slug = models.TextField(db_index=True, null=True, default=None)
    path = models.TextField(db_index=True, null=True, default=None)
    content = models.TextField(null=True, default=None)
    description = models.TextField(null=True, default=None)

    created = models.DateTimeField(db_index=True, default=timezone.now)
    edited = models.DateTimeField(db_index=True, null=True, default=None)
    published = models.DateTimeField(db_index=True, null=True, default=None)

    objects = CatalogElementManager()

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        self.slug = anodos.tools.to_slug(self.slug)
        if self.parent:
            self.path = f'{self.parent.path}/{self.slug}'
        else:
            self.path = self.slug
        self.edited = timezone.now()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created']


class ArticleManager(models.Manager):

    def create(self, title=None, slug=None, parent=None, image=None, assistant=False):

        if title is None:
            return None

        if slug:
            slug = anodos.tools.to_slug(slug)
        else:
            slug = anodos.tools.to_slug(title)

        try:
            image = Image.objects.get(id=image)
        except Image.DoesNotExist:
            return None

        try:
            parent = self.get(id=parent)
        except Article.DoesNotExist:
            parent = None

        o = super().create(parent=parent, title=title, slug=slug, image=image, assistant=assistant)

        return o


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey('CatalogElement', null=True, default=None,
                               on_delete=models.SET_NULL, related_name='+')
    image = models.ForeignKey('Image', null=True, default=None,
                              on_delete=models.SET_NULL, related_name='+')
    title = models.TextField(db_index=True)
    slug = models.TextField(db_index=True, null=True, default=None)
    path = models.TextField(db_index=True, null=True, default=None)
    content = models.TextField(null=True, default=None)
    description = models.TextField(null=True, default=None)

    assistant = models.BooleanField(db_index=True, default=False)

    created = models.DateTimeField(db_index=True, default=timezone.now)
    edited = models.DateTimeField(db_index=True, null=True, default=None)
    published = models.DateTimeField(db_index=True, null=True, default=None)

    objects = ArticleManager()

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        self.slug = anodos.tools.to_slug(self.slug)
        if self.parent:
            self.path = f'{self.parent.path}/{self.slug}'
        else:
            self.path = self.slug
        self.edited = timezone.now()

        super().save(*args, **kwargs)

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
        self.slug = anodos.tools.to_slug(name=self.name)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']


class UnitManager(models.Manager):

    def take(self, name, **kwargs):
        if not name:
            return None

        name = anodos.tools.fix_text(name)

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
    key_digit = models.CharField(max_length=32, null=True, default=None, unique=True)

    name = models.TextField(null=True, default=None, db_index=True)
    html = models.TextField(null=True, default=None, db_index=True)
    full_name = models.TextField(null=True, default=None, db_index=True)

    quantity = models.FloatField(null=True, default=None)
    rate = models.FloatField(null=True, default=None)

    objects = CurrencyManager()

    def __str__(self):
        if self.html is None:
            return f'{self.key}'
        else:
            return f'{self.html}'

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

    def save(self, *args, **kwargs):
        if self.value is not None:
            if float(self.value) > 10.0:
                self.value = int(self.value)
        super().save(*args, **kwargs)

    def create(self, *args, **kwargs):
        if self.value is not None:
            if float(self.value) > 10.0:
                self.value = int.self.value
        super().save(*args, **kwargs)

    @property
    def html(self):
        if self.value is not None:
            value = f'{self.value:,}'
            value = value.replace(',', '&nbsp;')
            value = value.replace('.', ',')
            return f'{value}&nbsp;{self.currency}'
        else:
            return None

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
        name = anodos.tools.fix_text(name)
        if name is not None and o.name is None:
            o.name = name
            need_save = True

        # short_name
        short_name = kwargs.get('short_name', None)
        short_name = anodos.tools.fix_text(short_name)
        if short_name is not None and o.short_name is None:
            o.short_name = short_name
            need_save = True

        # name_rus
        name_rus = kwargs.get('name_rus', None)
        name_rus = anodos.tools.fix_text(name_rus)
        if name_rus is not None and o.name_rus is None:
            o.name_rus = name_rus
            need_save = True

        # name_other
        name_other = kwargs.get('name_other', None)
        name_other = anodos.tools.fix_text(name_other)
        if name_other is not None and o.name_other is None:
            o.name_other = name_other
            need_save = True

        # description
        description = kwargs.get('description', None)
        description = anodos.tools.fix_text(description)
        if description is not None and o.description is None:
            o.description = description
            need_save = True

        # warranty
        warranty = kwargs.get('warranty', None)
        warranty = anodos.tools.fix_text(warranty)
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

    @property
    def url(self):
        if self.slug:
            url = f'{settings.HOST}/product/{self.slug}/'
            return url
        else:
            return None

    @property
    def url_xml(self):
        if self.slug:
            loc = f'{settings.HOST}/product/{self.slug}/'
            if self.quantity and self.price:
                priority = 1.0
            else:
                priority = 0.5
            url = f'    <url>\n' \
                  f'        <loc>{loc}</loc>\n' \
                  f'        <priority>{priority}</priority>\n' \
                  f'    </url>\n'
            return url
        else:
            return None

    @property
    def json(self):
        product = {'id': str(self.id),
                   'part_number': str(self.part_number),
                   'vendor': str(self.vendor),
                   'category': str(self.category),
                   'names_search': str(self.names_search),
                   'parameters_search': str(self.parameters_search),
                   'slug': str(self.slug),
                   'name': str(self.name),
                   'short_name': str(self.short_name),
                   'name_rus': str(self.name_rus),
                   'name_other': str(self.name_other),
                   'description': str(self.description),
                   'warranty': str(self.warranty),
                   'ean_128': str(self.ean_128),
                   'upc': str(self.upc),
                   'pnc': str(self.pnc),
                   'hs_code': str(self.hs_code),
                   'gtin': str(self.gtin),
                   'tnved': str(self.tnved),
                   'price': str(self.price),
                   'quantity': str(self.quantity),
                   'quantity_great_than': str(self.quantity_great_than),
                   'weight': str(self.weight),
                   'width': str(self.width),
                   'height': str(self.height),
                   'depth': str(self.depth),
                   'volume': str(self.volume),
                   'multiplicity': str(self.multiplicity),
                   'unit': str(self.unit),
                   'content': str(self.content),
                   'content_loaded': str(self.content_loaded),
                   'images_loaded': str(self.images_loaded),
                   'created': str(self.created),
                   'updated': str(self.updated),
                   'edited': str(self.edited),
                   }

        return product

    def save(self, *args, **kwargs):
        if self.vendor:
            self.names_search = f'{self.name.lower()} ' \
                          f'{self.part_number.lower()} ' \
                          f'{self.vendor.name.lower()}'
            self.slug = anodos.tools.to_slug(f'{self.vendor.name} {self.part_number}')
        else:
            self.names_search = f'{self.name.lower()} ' \
                          f'{self.part_number.lower()}'
            self.slug = anodos.tools.to_slug(f'{self.part_number}')
        self.updated = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created']
        indexes = [GinIndex(fields=['names_search', 'parameters_search'],
                            name='product_search_idx')]


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

    def save(self, *args, **kwargs):
        try:
            value_ = float(self.value)
            self.value = str(self.value)
            while '.' in self.value and self.value[-1] in ('0', '.',):
                self.value = self.value[:-1]
        except ValueError:
            pass
        except TypeError:
            pass

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created']


class ProductImageManager(models.Manager):

    width = 600
    height = 600

    def take(self, product, source_url, **kwargs):
        if not product or not source_url:
            return None

        source_url = anodos.tools.fix_text(source_url)

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

    def upload(self, bytes):

        im = PIL.Image.open(io.BytesIO(bytes))

        # Масштабируем исходное изображение
        dx = self.width / im.size[0]
        dy = self.height / im.size[1]
        d = min(dx, dy)
        im = im.resize((int(im.size[0]*d), int(im.size[1]*d)))

        # Создаём новое изображение и вставляем в него участок исходного
        im_new = PIL.Image.new('RGBA', (self.width, self.height), '#00000000')
        dx = (self.width - im.size[0]) // 2
        dy = (self.height - im.size[1]) // 2
        im_new.paste(im, (dx, dy))

        # Закрываем исходное изображение
        im.close()

        # Создаём объект изображения в базе
        image = self.create()
        image.file_name = f'{settings.MEDIA_ROOT}products/photos/{image.id}.png'
        image.create_directory_for_file()
        image.save()

        im_new.save(image.file_name, "PNG")
        im_new.close()

        return image


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
