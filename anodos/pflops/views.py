import json

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

import anodos.fixers
import pflops.models
import distributors.models


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