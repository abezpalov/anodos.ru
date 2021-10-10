import time
import requests as r
import lxml
import urllib.parse
from datetime import datetime, timedelta
import zeep

from django.utils import timezone
from django.conf import settings
from swarm.models import *
from swarm.workers.worker import Worker

import pflops.models
import distributors.models


class Worker(Worker):

    def __init__(self):

        super().__init__()

    def run(self, command=None):

        # Тесты
        # print(pflops.models.Product.objects.all().count())
        # print(distributors.models.Product.objects.filter(to_pflops__isnull=True).count())
        # print(distributors.models.Product.objects.filter(to_pflops__isnull=False).count())

        # Продукты
        # self.update_products()

        # Характеристики
        self.update_parameters()

        # Изображения

        # Количество

        # Цены

    def update_products(self):
        """ Переносит сущность продукт в чистовик """

        ids_ = distributors.models.Product.objects.filter(vendor__to_pflops__isnull=False).values('id')
        for n, id_ in enumerate(ids_):
            product_ = distributors.models.Product.objects.get(id=id_['id'])

            if product_.category is not None:
                category = product_.category.to_pflops
            else:
                category = None

            if product_.unit is not None:
                unit = product_.unit.to_pflops
            else:
                unit = None

            product = pflops.models.Product.objects.take(vendor=product_.vendor.to_pflops,
                                                         part_number=product_.part_number,
                                                         category=category,
                                                         name=product_.name,
                                                         short_name=product_.short_name,
                                                         name_rus=product_.name_rus,
                                                         name_other=product_.name_other,
                                                         description=product_.description,
                                                         warranty=product_.warranty,
                                                         ean_128=product_.ean_128,
                                                         upc=product_.upc,
                                                         pnc=product_.pnc,
                                                         hs_code=product_.hs_code,
                                                         gtin=product_.gtin,
                                                         tnved=product_.tnved,
                                                         traceable=product_.traceable,
                                                         unconditional=product_.unconditional,
                                                         sale=product_.sale,
                                                         promo=product_.promo,
                                                         outoftrade=product_.outoftrade,
                                                         condition_description=product_.condition_description,
                                                         weight=product_.weight,
                                                         width=product_.width,
                                                         height=product_.height,
                                                         depth=product_.depth,
                                                         volume=product_.volume,
                                                         multiplicity=product_.multiplicity,
                                                         unit=unit,
                                                         content=product_.content,
                                                         content_loaded=product_.content_loaded)
            if product_.to_pflops != product:
                product_.to_pflops = product
                product_.save()
            print(f'{n + 1} of {len(ids_)} {product}')

    def update_parameters(self):

        # Удаляем мусор
        distributors.models.Parameter.objects.filter(distributor__isnull=True).delete()

        # Удаляем дубли и кривой текст
        parameters = distributors.models.Parameter.objects.all()
        for n, parameter in enumerate(parameters):
            print(f'{n+1} of {len(parameters)} {parameter}')

            if self.fix_text(parameter.name) != parameter.name:
                parameter.delete()
                continue

            parameters_ = distributors.models.Parameter.objects.filter(distributor=parameter.distributor,
                                                                       name=parameter.name)
            for m, parameter_ in enumerate(parameters_):
                if m > 0:
                    parameter_.delete()

        # Проходим по все продуктам
        ids_ = pflops.models.Product.objects.all().values('id')
        for n, id_ in enumerate(ids_):
            product = pflops.models.Product.objects.get(id=id_['id'])

            # Выбираем источник для переноса параметоров в чистовик
            max_parameters_count = -1
            product_ = None
            for p_ in distributors.models.Product.objects.filter(to_pflops=product):
                parameters_count = distributors.models.ParameterValue.filter(product=p_).count()
                if parameters_count > max_parameters_count:
                    product_ = p_

            # Получаем ID текущих значений характеристик (чтобы потом удалить необновленные)
            parameter_values_ids_ = pflops.models.ParameterValue.filter(product=product_).values('id')
            parameter_values_ids = set()
            for parameter_values_id_ in parameter_values_ids_:
                parameter_values_ids.add(parameter_values_id_['id'])

            # Переносим параметры
            parameter_values_ = distributors.models.ParameterValue.filter(product=product_)





