from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

import anodos.fixers
import pflops.models


def view_search(request):
    if request.method == 'POST':
        search = request.POST.get('search', None)
        if search:
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
