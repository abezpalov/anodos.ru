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


def product(request, product_id):

    item = distributors.models.Product.objects.get(id=product_id)

    params = distributors.models.ParameterValue.objects.filter(product=item)
    images = distributors.models.ProductImage.objects.filter(product=item)

    context = {'product': item, 'params': params, 'images': images}

    return render(request, 'distributors/product.html', context)


def vendors(request):
    if request.user.has_perm('distributors.change_vendor'):
        items = distributors.models.Vendor.objects.all()
        pflops_vendors = pflops.models.Vendor.objects.all()

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
    distributors_vendor_id = request.POST.get('id', None)
    try:
        distributors_vendor = distributors.models.Vendor.objects.get(
            id=distributors_vendor_id)
    except distributors.models.Vendor.DoesNotExist:
        return HttpResponse(status=404)

    # Привязываем к нашему производителю
    try:
        pflops_vendor = pflops.models.Vendor.objects.get(
            name=distributors_vendor.name)
    except pflops.models.Vendor.DoesNotExist:
        pflops_vendor = pflops.models.Vendor.objects.create(
            name=distributors_vendor.name)
    distributors_vendor.pflops_vendor = pflops_vendor
    distributors_vendor.save()

    # Готовим ответ
    result = {'status': 'success',
              'id': str(pflops_vendor.id),
              'name': str(pflops_vendor.name)}

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
    distributors_vendor_id = request.POST.get('id', None)
    try:
        distributors_vendor = distributors.models.Vendor.objects.get(
            id=distributors_vendor_id)
    except distributors.models.Vendor.DoesNotExist:
        return HttpResponse(status=404)

    # Отвязываем от нашего производителя
    distributors_vendor.pflops_vendor = None
    distributors_vendor.save()

    # Готовим ответ
    result = {'status': 'success'}

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
