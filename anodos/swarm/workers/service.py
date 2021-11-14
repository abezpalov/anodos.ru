import PIL
import numpy as np
from datetime import datetime

from django.conf import settings

import anodos.tools
import swarm.models
import pflops.models
import distributors.models
import swarm.workers.worker


class Worker(swarm.workers.worker.Worker):

    name = 'Service'

    def __init__(self):
        self.count_of_products = 0
        self.count_of_parties = 0
        self.count_of_parameters = 0
        self.count_of_images = 0
        self.count_of_urls = 0
        self.message = None
        super().__init__()

    def run(self):

        if self.command == 'info':
            print('Продуктов в PFLOPS:',
                  pflops.models.Product.objects.all().count())
            print('Продуктов не перенесено от дистрибьюторов:',
                  distributors.models.Product.objects.filter(to_pflops__isnull=True).count())
            print('Продуктов перенесено от дистрибьюторов:',
                  distributors.models.Product.objects.filter(to_pflops__isnull=False).count())

        elif self.command == 'update_products':

            # Обновляем продукты
            self.update_products()

            # Обновляем цены и наличие
            self.update_prices_and_quantities()

            # Готовим оповещение
            self.message = f'- продуктов: {self.count_of_products};\n' \
                           f'- партий: {self.count_of_parties}.'

        elif self.command == 'update_parameters':
            # Характеристики
            self.update_parameters()

            # Готовим оповещение
            self.message = f'- параметров: {self.count_of_parameters}.'

        elif self.command == 'update_images':

            # Изображения
            self.update_images()

            # Готовим оповещение
            self.message = f'- изображений: {self.count_of_images}.'

        elif self.command == 'rewrite_products':
            ids_ = pflops.models.Product.objects.all().values('id')
            for n, id_ in enumerate(ids_):
                product = pflops.models.Product.objects.get(id=id_['id'])
                print(f'{n + 1} of {len(ids_)} {product}')
                product.save()

        elif self.command == 'rewrite_parameter_values':
            ids_ = pflops.models.ParameterValue.objects.all().values('id')
            for n, id_ in enumerate(ids_):
                value = pflops.models.ParameterValue.objects.get(id=id_['id'])
                print(f'{n + 1} of {len(ids_)} {value}')
                value.save()

        elif self.command == 'del_all_images':
            pflops.models.ProductImage.objects.all().delete()

        elif self.command == 'update_sitemap':
            self.update_sitemap()

            # Готовим оповещение
            self.message = f'- ссылок: {self.count_of_urls}.'

        else:
            print('Неизвестная команда!')

        if self.message:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}:\n'
                                      f'{self.message}')
        else:
            anodos.tools.send(content=f'{self.name}: {self.command} finish at {self.delta()}.\n')

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
                                                         weight=product_.weight,
                                                         width=product_.width,
                                                         height=product_.height,
                                                         depth=product_.depth,
                                                         volume=product_.volume,
                                                         multiplicity=product_.multiplicity,
                                                         unit=unit,
                                                         content=product_.content)
            if product_.to_pflops != product:
                product_.to_pflops = product
                product_.save()

            self.count_of_products += 1

            print(f'{n + 1} of {len(ids_)} {product}')

    def update_prices_and_quantities(self):

        rub_ = distributors.models.Currency.objects.take(key="RUB")
        rub = pflops.models.Currency.objects.take(key="RUB")

        ids_ = pflops.models.Product.objects.all().values('id')
        for n, id_ in enumerate(ids_):
            product = pflops.models.Product.objects.get(id=id_['id'])

            parties = distributors.models.Party.objects.filter(product__to_pflops=product)
            price = None
            quantity = 0
            quantity_great_than = False

            # Цены
            for party in parties:
                if party.quantity:
                    if party.price_out_open:
                        if party.price_out_open.currency == rub_:
                            price = party.price_out_open.value
                        else:
                            price = float(party.price_out_open.value) * float(party.price_out_open.currency.rate) / \
                                    float(party.price_out_open.currency.quantity)
                        break

                    elif party.price_in:
                        if party.price_in.currency == rub_:
                            price_ = float(party.price_in.value) * settings.MARGIN
                        else:
                            price_ = float(party.price_in.value) * float(party.price_in.currency.rate) / \
                                    float(party.price_in.currency.quantity) * settings.MARGIN
                        if price is None or price_ < price:
                            price = price_

            # Количество
            for party in parties:
                if party.quantity:
                    quantity += party.quantity

                    if party.quantity_great_than:
                        quantity_great_than = True

            if price is not None:
                price = pflops.models.Price.objects.create(value=price, currency=rub)
            product.price = price
            product.quantity = quantity
            product.quantity_great_than = quantity_great_than
            product.save()

            print(f'{n + 1} of {len(ids_)} {product} | {product.quantity} | {product.price}')

            self.count_of_parties += 1

    def update_parameters(self):

        # Удаляем мусор
        distributors.models.Parameter.objects.filter(distributor__isnull=True).delete()

        # Удаляем дубли и кривой текст
        parameters = distributors.models.Parameter.objects.all()
        for n, parameter in enumerate(parameters):
            print(f'{n+1} of {len(parameters)} {parameter}')

            if anodos.tools.fix_text(parameter.name) != parameter.name:
                parameter.delete()
                continue

            parameters_ = distributors.models.Parameter.objects.filter(distributor=parameter.distributor,
                                                                       name=parameter.name)
            for m, parameter_ in enumerate(parameters_):
                if m > 0:
                    parameter_.delete()

        # Проходим по всем продуктам
        ids_ = pflops.models.Product.objects.all().values('id')
        for n, id_ in enumerate(ids_):
            product = pflops.models.Product.objects.get(id=id_['id'])
            print(f'{n + 1} of {len(ids_)} {product}')

            # Выбираем источник для переноса параметоров в чистовик
            max_parameters_count = -1
            product_ = None
            for p_ in distributors.models.Product.objects.filter(to_pflops=product):
                parameters_count = distributors.models.ParameterValue.objects.filter(product=p_).count()
                if parameters_count > max_parameters_count:
                    product_ = p_

            # Получаем ID текущих значений характеристик (чтобы потом удалить неактуальные)
            parameter_values_ids_ = pflops.models.ParameterValue.objects.filter(product=product).values('id')
            parameter_values_ids = set()
            for parameter_values_id_ in parameter_values_ids_:
                parameter_values_ids.add(str(parameter_values_id_['id']))

            # Переносим параметры
            parameter_values_ = distributors.models.ParameterValue.objects.filter(product=product_)
            for parameter_value_ in parameter_values_:
                if parameter_value_.parameter is not None:
                    parameter = parameter_value_.parameter.to_pflops
                else:
                    continue
                if parameter_value_.unit is not None:
                    unit = parameter_value_.unit.to_pflops
                else:
                    unit = None

                # TODO Сделать дополнительную обработку при выборе единицы измерения

                value = parameter_value_.value
                parameter_value = pflops.models.ParameterValue.objects.take(product=product,
                                                                            parameter=parameter,
                                                                            value=value,
                                                                            unit=unit)
                if parameter_value is not None:
                    if str(parameter_value.id) in parameter_values_ids:
                        parameter_values_ids.remove(str(parameter_value.id))

                    self.count_of_parameters += 1

            # Удаляем устаревшие параметры
            for parameter_values_id in parameter_values_ids:
                pflops.models.ParameterValue.objects.filter(id=parameter_values_id).delete()

    def update_images(self):

        # Проходим по всем продуктам
        ids_ = pflops.models.Product.objects.all().values('id')
        # ids_ = pflops.models.Product.objects.filter(images_loaded__isnull=True).values('id')
        for n, id_ in enumerate(ids_):

            product = pflops.models.Product.objects.get(id=id_['id'])
            print(f'{n + 1} of {len(ids_)} {product}')

            self.update_images_of_product(product)

    def update_images_of_product(self, product):

        # Получаем векторы для сравнения из базы имеющихся изображений
        vs = []
        images = pflops.models.ProductImage.objects.filter(product=product)
        for image in images:

            # Если изображение уже есть
            if image.file_name:

                # Загружаем изображение
                try:
                    im = PIL.Image.open(image.file_name)
                except FileNotFoundError:
                    continue
                except PIL.UnidentifiedImageError:
                    continue

                # Сравниваем изображения с имеющимися
                copy = False
                thumbnail_ = im.resize((42, 42))
                v_ = np.array(thumbnail_).reshape(42 * 42 * 4)
                for v in vs:
                    r = np.dot(v, v_) / (np.linalg.norm(v) * np.linalg.norm(v_))
                    if r < 1.0e-11:
                        copy = True

                # Если это копия
                if copy is True:
                    image.delete()
                else:
                    vs.append(v_)

        # Проходим по всех исходным продуктам у дистрибьюторов
        for product_ in distributors.models.Product.objects.filter(to_pflops=product):

            # Проходим по всем изображениям
            images_ = distributors.models.ProductImage.objects.filter(product=product_)
            for image_ in images_:

                # Берём сущность с базы
                image = pflops.models.ProductImage.objects.take(product=product,
                                                                source_url=image_.source_url)

                if image.file_name:
                    continue

                # Открываем исходное изображение и проверяем, достаточный ли размер изображения
                try:
                    im = PIL.Image.open(image_.file_name)
                except ValueError:
                    continue
                except AttributeError:
                    continue
                except PIL.UnidentifiedImageError:
                    continue

                if im.size[0] < 450 and im.size[1] < 450:
                    im.close()
                    continue

                # Вычисляем размеры и координаты
                size = max(im.size[0], im.size[1])
                dx = (size - im.size[0]) // 2
                dy = (size - im.size[1]) // 2

                # Создаём новое изображение и масштабируем его
                try:
                    im_new = PIL.Image.new('RGBA', (size, size), '#00000000')
                    im_new.paste(im, (dx, dy))
                    im_new = im_new.resize((600, 600))
                except SyntaxError:
                    im.close()
                    im_new.close()
                    image.delete()
                    continue
                except OSError:
                    im.close()
                    im_new.close()
                    image.delete()
                    continue

                # Сравниваем изображения с имеющимися
                copy = False
                thumbnail_ = im_new.resize((42, 42))
                v_ = np.array(thumbnail_).reshape(42*42*4)
                for v in vs:
                    r = np.dot(v, v_) / (np.linalg.norm(v) * np.linalg.norm(v_))
                    if r < 1.0e-12:
                        copy = True

                if copy is True:
                    im.close()
                    im_new.close()
                    image.delete()
                else:
                    vs.append(v_)

                    image.file_name = f'{settings.MEDIA_ROOT}products/photos/{image.id}.png'
                    image.create_directory_for_file()
                    im_new.save(image.file_name, "PNG")
                    image.save()

                    print(image)

                    im.close()
                    im_new.close()

                    self.count_of_images += 1

    def update_sitemap(self):

        print('update_sitemap')

        count_of_urls = 0
        count_of_urlsets = 0
        urls_in_urlset = 25000

        urlsets_str = ''
        urlset_str = ''

        products = pflops.models.Product.objects.all()

        for n, product in enumerate(products):
            print(f'{n+1} of {len(products)} {product.url}')
            if product.url_xml:
                urlset_str = f'{urlset_str}{product.url_xml}'
                count_of_urls += 1

            if (count_of_urls and count_of_urls % urls_in_urlset == 0) or n + 1 == len(products):
                urlset_filename = f'{settings.STATIC_ROOT}sitemap/sitemap-{count_of_urlsets}.xml'
                urlset_url = f'{settings.HOST}{settings.STATIC_URL}sitemap/sitemap-{count_of_urlsets}.xml'
                urlsets_str = f'{urlsets_str}\n' \
                              f'    <sitemap>\n' \
                              f'        <loc>{urlset_url}</loc>\n' \
                              f'        <lastmod>{str(datetime.now())}</lastmod>\n' \
                              f'    </sitemap>\n'
                count_of_urlsets += 1

                urlset_str = f'<?xml version="1.0" encoding="UTF-8"?>\n' \
                             f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' \
                             f'{urlset_str}' \
                             f'</urlset>\n'

                anodos.tools.create_directory_for_file(urlset_filename)
                urlset_file = open(urlset_filename, 'w')
                urlset_file.write(urlset_str)
                urlset_file.close()

                urlset_str = ''

        urlsets_str = f'<?xml version="1.0" encoding="UTF-8"?>\n' \
                      f'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' \
                      f'{urlsets_str}' \
                      f'</sitemapindex>\n'

        urlsets_filename = f'{settings.STATIC_ROOT}sitemap/sitemap.xml'
        anodos.tools.create_directory_for_file(urlsets_filename)
        urlset_files = open(urlsets_filename, 'w')
        urlset_files.write(urlsets_str)
        urlset_files.close()

        self.count_of_urls = count_of_urls
