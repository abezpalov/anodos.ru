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

        self.update_products()

    def update_products(self):

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
            print(f'{n+1} of {len(ids_)} {product}')


            # quantity

            # price

            # properties

            # images


