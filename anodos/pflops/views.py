
import json
import telebot

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

import anodos.fixers
import pflops.models
import distributors.models


def view_index(request):
    catalog_elements = pflops.models.CatalogElement.objects.all().order_by('created')
    assistant_elements = pflops.models.Article.objects.filter(assistant=True).order_by('-created')

    return render(request, 'main.html', locals())


def view_search(request):
    if request.method == 'POST':
        search = request.POST.get('search', '')
        if len(search) > 1:
            words = anodos.fixers.string_to_words(search)
            qs = [Q(quantity__gt=0)]
            for word in words:
                if word:
                    qs.append(Q(names_search__icontains=word))
            for n, q_ in enumerate(qs):
                if n == 0:
                    q = q_
                else:
                    q = q & q_
            products = pflops.models.Product.objects.filter(q)

    return render(request, 'pflops/search.html', locals())


def view_product(request, product_slug):

    product = pflops.models.Product.objects.get(slug=product_slug)

    params = pflops.models.ParameterValue.objects.filter(product=product)
    images = pflops.models.ProductImage.objects.filter(product=product, file_name__isnull=False)

    context = {'product': product, 'params': params, 'images': images}

    return render(request, 'pflops/product.html', locals())


def article(request, slug):
    item = pflops.models.Article.objects.get(slug=slug)

    context = {'item': item}
    return render(request, 'pflops/article.html', locals())


def vendors(request):
    items = pflops.models.Vendor.objects.all()

    context = {'items': items}
    return render(request, 'pflops/vendors.html', locals())


def ajax_get_parties(request):

    # Проверяем тип запроса
    if not request.is_ajax():
        return HttpResponse(status=400)

    # Получаем экземпляр продукта
    product = request.POST.get('product', None)
    try:
        product = pflops.models.Product.objects.get(id=product)
    except pflops.models.Product.DoesNotExist:
        return HttpResponse(status=404)

    parties = distributors.models.Party.objects.filter(product__to_pflops=product)

    html = '<table>' \
           '<thead><tr><th>Тест</th></tr>' \
           '</table>'

    # Готовим ответ
    result = {'status': 'success',
              'product': str(product.id),
              'html': html}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


@csrf_exempt
def ajax_load_catalog_element_image(request):

    # Проверяем права доступа
    if not request.user.has_perm('pflops.can_change'):
        return HttpResponse(status=403)

    message = []
    items = request.FILES.items()
    for _, file in items:

        bytes = file.read()
        image = pflops.models.Image.objects.take(bytes, style='catalog')

        message = str(image)

    # Готовим ответ
    result = {'status': 'success',
              'id': str(image.id),
              'url': str(image.url)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_save_new_catalog_element(request):

    # Проверяем тип запроса
    if not request.POST:
        return HttpResponse(status=400)

    # title
    title = request.POST.get('title', None)

    # slug
    slug = request.POST.get('slug', None)

    # image
    image = request.POST.get('image', None)

    parent = request.POST.get('parent', None)

    catalog_element = pflops.models.CatalogElement.objects.create(parent=parent,
                                                                  title=title,
                                                                  slug=slug,
                                                                  image=image)
    if catalog_element is None:
        return HttpResponse(status=400)

    # Готовим ответ
    result = {'status': 'success',
              'id': str(catalog_element.id),
              'title': str(catalog_element.title),
              'image': str(catalog_element.image)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


@csrf_exempt
def ajax_load_assistant_element_image(request):

    # Проверяем права доступа
    if not request.user.has_perm('pflops.can_change'):
        return HttpResponse(status=403)

    message = []
    items = request.FILES.items()
    for _, file in items:

        bytes = file.read()
        image = pflops.models.Image.objects.take(bytes, style='assistant')

        message = str(image)

    # Готовим ответ
    result = {'status': 'success',
              'id': str(image.id),
              'url': str(image.url)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')


def ajax_save_new_assistant_element(request):

    # Проверяем тип запроса
    if not request.POST:
        return HttpResponse(status=400)

    # title
    title = request.POST.get('title', None)

    # slug
    slug = request.POST.get('slug', None)

    # image
    image = request.POST.get('image', None)

    parent = request.POST.get('parent', None)

    assistant = pflops.models.Article.objects.create(parent=parent,
                                                     title=title,
                                                     slug=slug,
                                                     image=image,
                                                     assistant=True)
    if assistant is None:
        return HttpResponse(status=400)

    # Готовим ответ
    result = {'status': 'success',
              'id': str(assistant.id),
              'title': str(assistant.title),
              'image': str(assistant.image)}

    # Возмращаем результат
    return HttpResponse(json.dumps(result), 'application/javascript')
