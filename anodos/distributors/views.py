import json

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

import distributors.models
import pflops.models


def index(request):

    context = {}

    if request.method == 'POST':
        search = request.POST.get('search', None)
        if search:
            words = string_to_words(search)
            qs = []
            for word in words:
                if word:
                    qs.append(Q(search__icontains=word))
            if qs:
                for n, q_ in enumerate(qs):
                    if n == 0:
                        q = q_
                    else:
                        q = q & q_
            parties = distributors.models.Party.objects.filter(q)
            context = {'search': search,
                       'parties': parties,
                       }

    return render(request, 'distributors/search.html', context)


def view_product(request, product_id):

    product = distributors.models.Product.objects.get(id=product_id)

    params = distributors.models.ParameterValue.objects.filter(product=product)
    images = distributors.models.ProductImage.objects.filter(product=product)

    context = {'product': product, 'params': params, 'images': images}

    return render(request, 'distributors/product.html', context)


def view_vendors(request):
    if request.user.has_perm('distributors.change_vendor'):
        vendors_ = distributors.models.Vendor.objects.all()
        vendors = pflops.models.Vendor.objects.all()

        return render(request, 'distributors/vendors.html', locals())
    else:
        return HttpResponse(status=403)


def ajax_vendor_as_is(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.change_vendor'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    vendor_ = request.POST.get('vendor_', None)
    try:
        vendor_ = distributors.models.Vendor.objects.get(id=vendor_)
    except distributors.models.Vendor.DoesNotExist:
        return HttpResponse(status=404)

    # Привязываем к нашему производителю
    try:
        vendor = pflops.models.Vendor.objects.get(name__iexact=vendor_.name)
    except pflops.models.Vendor.DoesNotExist:
        vendor = pflops.models.Vendor.objects.create(name=vendor_.name)
    vendor_.to_pflops = vendor
    vendor_.save()

    # Готовим ответ
    result = {'status': 'success',
              'vendor_': str(vendor_.id),
              'vendor': str(vendor.id),
              'name': str(vendor.name)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_erase_vendor_link(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.change_vendor'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    vendor_ = request.POST.get('vendor_', None)
    try:
        vendor_ = distributors.models.Vendor.objects.get(id=vendor_)
    except distributors.models.Vendor.DoesNotExist:
        return HttpResponse(status=404)

    # Отвязываем от нашего производителя
    vendor_.to_pflops = None
    vendor_.save()

    # Готовим ответ
    result = {'status': 'success',
              'vendor_': str(vendor_.id)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_link_vendor(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.change_vendor'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    vendor_ = request.POST.get('vendor_', None)
    try:
        vendor_ = distributors.models.Vendor.objects.get(id=vendor_)
    except distributors.models.Vendor.DoesNotExist:
        return HttpResponse(status=404)

    # Получаем экземпляр производителя
    vendor = request.POST.get('vendor', None)
    try:
        vendor = pflops.models.Vendor.objects.get(id=vendor)
    except distributors.models.Vendor.DoesNotExist:
        return HttpResponse(status=404)

    vendor_.to_pflops = vendor
    vendor_.save()

    # Готовим ответ
    result = {'status': 'success',
              'vendor_': str(vendor_.id),
              'name': str(vendor.name)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_save_vendor(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.change_vendor'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    vendor = request.POST.get('vendor', None)
    try:
        vendor = pflops.models.Vendor.objects.get(id=vendor)
    except pflops.models.Vendor.DoesNotExist:
        return HttpResponse(status=404)

    name = request.POST.get('name', None)
    vendor.name = name
    vendor.save()

    # Готовим ответ
    result = {'status': 'success',
              'id': str(vendor.id),
              'name': str(vendor.name)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def string_to_words(name):
    name = name.lower()

    dictionary = {',': ' ', '?': ' ', '~': ' ', '!': ' ', '@': ' ', '#': ' ', '$': ' ',
                  '%': ' ', '^': ' ', '&': ' ', '*': ' ', '(': ' ', ')': ' ', '=': ' ',
                  '+': ' ', ':': ' ', ';': ' ', '<': ' ', '>': ' ', '\'': ' ', '"': ' ',
                  '\\': ' ', '/': ' ', '№': ' ', '[': ' ', ']': ' ', '{': ' ', '}': '-',
                  'ґ': ' ', 'ї': ' ', 'є': ' ', 'Ґ': ' ', 'Ї': ' ', 'Є': ' ', '—': ' ',
                  '\t': ' ', '\n': ' ', }

    for key in dictionary:
        name = name.replace(key, dictionary[key])

    while '  ' in name:
        name = name.replace('  ', ' ')

    name = name.strip()

    return name.split(' ')
