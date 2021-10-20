import json

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

import anodos.fixers
import distributors.models
import pflops.models


def index(request):

    context = {}

    if request.method == 'POST':
        search = request.POST.get('search', None)
        if search:
            words = anodos.fixers.string_to_words(search)
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


def view_categories(request):
    if request.user.has_perm('distributors.change_category'):
        categories_ = distributors.models.Category.objects.all()
        categories = pflops.models.Category.objects.all()
        return render(request, 'distributors/categories.html', locals())
    else:
        return HttpResponse(status=403)


def view_parameters(request):
    if request.user.has_perm('distributors.change_parameter'):
        parameters_ = distributors.models.Parameter.objects.all()
        parameters = pflops.models.Parameter.objects.all()
        return render(request, 'distributors/parameters.html', locals())
    else:
        return HttpResponse(status=403)


def view_units(request):
    if request.user.has_perm('distributors.change_unit'):
        units_ = distributors.models.ParameterUnit.objects.all()
        units = pflops.models.Unit.objects.all()
        return render(request, 'distributors/units.html', locals())
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
    except pflops.models.Vendor.MultipleObjectsReturned:
        vendors = pflops.models.Vendor.objects.filter(name__iexact=vendor_.name)
        for n, v in enumerate(vendors):
            if n == 0:
                vendor = v
            else:
                v.delete()

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


def ajax_parameter_as_is(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.parameter'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    parameter_ = request.POST.get('parameter_', None)
    try:
        parameter_ = distributors.models.Parameter.objects.get(id=parameter_)
    except distributors.models.Parameter.DoesNotExist:
        return HttpResponse(status=404)

    # Привязываем к нашему производителю
    try:
        parameter = pflops.models.Parameter.objects.get(name__iexact=parameter_.name)
    except pflops.models.Parameter.DoesNotExist:
        parameter = pflops.models.Parameter.objects.create(name=parameter_.name)
    except pflops.models.Parameter.MultipleObjectsReturned:
        parameters = pflops.models.Parameter.objects.filter(name__iexact=parameter_.name)
        for n, v in enumerate(parameters):
            if n == 0:
                parameter = v
            else:
                v.delete()

    parameter_.to_pflops = parameter
    parameter_.save()

    # Готовим ответ
    result = {'status': 'success',
              'parameter_': str(parameter_.id),
              'parameter': str(parameter.id),
              'name': str(parameter.name)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_erase_parameter_link(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.change_parameter'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    parameter_ = request.POST.get('parameter_', None)
    try:
        parameter_ = distributors.models.Parameter.objects.get(id=parameter_)
    except distributors.models.Parameter.DoesNotExist:
        return HttpResponse(status=404)

    # Отвязываем от нашего производителя
    parameter_.to_pflops = None
    parameter_.save()

    # Готовим ответ
    result = {'status': 'success',
              'parameter_': str(parameter_.id)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_link_parameter(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.change_parameter'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    parameter_ = request.POST.get('parameter_', None)
    try:
        parameter_ = distributors.models.Parameter.objects.get(id=parameter_)
    except distributors.models.Parameter.DoesNotExist:
        return HttpResponse(status=404)

    # Получаем экземпляр производителя
    parameter = request.POST.get('parameter', None)
    try:
        parameter = pflops.models.Parameter.objects.get(id=parameter)
    except distributors.models.Parameter.DoesNotExist:
        return HttpResponse(status=404)

    parameter_.to_pflops = parameter
    parameter_.save()

    # Готовим ответ
    result = {'status': 'success',
              'parameter_': str(parameter_.id),
              'name': str(parameter.name)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_save_parameter(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.change_parameter'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    parameter = request.POST.get('parameter', None)
    try:
        parameter = pflops.models.Parameter.objects.get(id=parameter)
    except pflops.models.Parameter.DoesNotExist:
        return HttpResponse(status=404)

    name = request.POST.get('name', None)
    parameter.name = name
    parameter.save()

    # Готовим ответ
    result = {'status': 'success',
              'id': str(parameter.id),
              'name': str(parameter.name)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_unit_as_is(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.unit'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    unit_ = request.POST.get('unit_', None)
    try:
        unit_ = distributors.models.ParameterUnit.objects.get(id=unit_)
    except distributors.models.ParameterUnit.DoesNotExist:
        return HttpResponse(status=404)

    # Привязываем к нашему производителю
    try:
        unit = pflops.models.Unit.objects.get(name__iexact=unit_.name)
    except pflops.models.Unit.DoesNotExist:
        unit = pflops.models.Unit.objects.create(name=unit_.name)
    except pflops.models.Unit.MultipleObjectsReturned:
        units = pflops.models.Unit.objects.filter(name__iexact=unit_.name)
        for n, v in enumerate(units):
            if n == 0:
                unit = v
            else:
                v.delete()

    unit_.to_pflops = unit
    unit_.save()

    # Готовим ответ
    result = {'status': 'success',
              'unit_': str(unit_.id),
              'unit': str(unit.id),
              'name': str(unit.name)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_erase_unit_link(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.change_unit'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    unit_ = request.POST.get('unit_', None)
    try:
        unit_ = distributors.models.ParameterUnit.objects.get(id=unit_)
    except distributors.models.ParameterUnit.DoesNotExist:
        return HttpResponse(status=404)

    # Отвязываем от нашего производителя
    unit_.to_pflops = None
    unit_.save()

    # Готовим ответ
    result = {'status': 'success',
              'unit_': str(unit_.id)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_link_unit(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.change_unit'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    unit_ = request.POST.get('unit_', None)
    try:
        unit_ = distributors.models.ParameterUnit.objects.get(id=unit_)
    except distributors.models.ParameterUnit.DoesNotExist:
        return HttpResponse(status=404)

    # Получаем экземпляр производителя
    unit = request.POST.get('unit', None)
    try:
        unit = pflops.models.Unit.objects.get(id=unit)
    except pflops.models.Unit.DoesNotExist:
        return HttpResponse(status=404)

    unit_.to_pflops = unit
    unit_.save()

    # Готовим ответ
    result = {'status': 'success',
              'unit_': str(unit_.id),
              'name': str(unit.name)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_save_unit(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Проверяем права доступа
    if not request.user.has_perm('distributors.change_unit'):
        return HttpResponse(status=403)

    # Получаем экземпляр производителя у дистрибьюторов
    unit = request.POST.get('unit', None)
    try:
        unit = pflops.models.Unit.objects.get(id=unit)
    except pflops.models.Unit.DoesNotExist:
        return HttpResponse(status=404)

    name = request.POST.get('name', None)
    unit.name = name
    unit.save()

    # Готовим ответ
    result = {'status': 'success',
              'id': str(unit.id),
              'name': str(unit.name)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')
