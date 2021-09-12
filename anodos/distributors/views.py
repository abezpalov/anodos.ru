from django.shortcuts import render
from django.http import HttpResponse

from .models import Distributor, Product


def index(request):
    distributors = Distributor.objects.all()
    context = {'distributors': distributors}
    return render(request, 'distributors/index.html', context)


def product(request, distributor, vendor, article):

    product = Product.objects.get(distributor__slug=distributor,
                                  vendor__slug=vendor,
                                  slug=article)

    context = {'distributor': distributor,
               'vendor': vendor,
               'article': article,
               'product': product}

    return render(request, 'distributors/product.html', context)
