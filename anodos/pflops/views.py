from django.shortcuts import render
from django.http import HttpResponse

import pflops.models


def article(request, slug):
    item = pflops.models.Article.objects.get(slug=slug)

    context = {'item': item}
    return render(request, 'pflops/article.html', locals())


def vendors(request):
    items = pflops.models.Vendor.objects.all()

    context = {'items': items}
    return render(request, 'pflops/vendors.html', locals())


def view_product(request, product_slug):

    product = pflops.models.Product.objects.get(slug=product_slug)

    params = pflops.models.ParameterValue.objects.filter(product=product)
    images = pflops.models.ProductImage.objects.filter(product=product)

    context = {'product': product, 'params': params, 'images': images}

    return render(request, 'pflops/product.html', locals())
