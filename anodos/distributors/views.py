from django.shortcuts import render
from django.http import HttpResponse

from .models import Distributor, Product, Party, ParameterValue, ProductImage


def index(request):
    distributors = Distributor.objects.all()
    context = {'distributors': distributors}
    return render(request, 'distributors/index.html', context)


def product(request, product_id):

    item = Product.objects.get(id=product_id)

    params = ParameterValue.objects.filter(product=item)
    images = ProductImage.objects.filter(product=item)

    context = {'product': item, 'params': params, 'images': images}

    return render(request, 'distributors/product.html', context)
