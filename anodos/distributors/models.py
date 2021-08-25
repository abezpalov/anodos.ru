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

    def take(self, distributor, name, parent=None):
        if not distributor or not name:
            return None
        try:
            o = self.get(distributor=distributor, name=name)
        except Category.DoesNotExist:
            o = Category()
            o.distributor = distributor
            o.name = name
            o.parent = parent
            if parent is None:
                o.level = 0
            else:
                o.level = parent.level + 1

        o.save()
        return o

    def get_by_article(self, distributor, article):
        try:
            o = self.get(distributor=distributor, name__cotains=f'[{article}]')
        except Category.DoesNotExist:
            return None
        return o


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey('Distributor', null=True, default=None,
                                    on_delete=models.CASCADE, related_name='+')
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


#class Product(models.Model):
#    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#    key = models.TextField(db_index=True, null=True, default=None)
#    part_number = models.TextField(db_index=True, null=True, default=None)
#    distributor = models.ForeignKey('Distributor', null=True, default=None,
#                                    on_delete=models.CASCADE, related_name='+')
#    vendor = models.ForeignKey('Vendor', null=True, default=None,
#                               on_delete=models.CASCADE, related_name='+')
#    category = models.ForeignKey('Category', null=True, default=None,
#                                 on_delete=models.CASCADE, related_name='+')
#    name = models.TextField(db_index=True)
#    name_rus = models.TextField(db_index=True, null=True, default=None)
#    name_other = models.TextField(db_index=True, null=True, default=None)
#    description = models.TextField(db_index=True, null=True, default=None)

#    eaN128 = models.TextField(db_index=True, null=True, default=None)
#    upc = models.TextField(db_index=True, null=True, default=None)
#    pnc = models.TextField(db_index=True, null=True, default=None)
#    hsCode = models.TextField(db_index=True, null=True, default=None)

#    traceable = models.BooleanField(null=True, default=None)

#    condition = models.TextField(db_index=True, null=True, default=None)
#    condition_description = models.TextField(null=True, default=None)
