from django.shortcuts import render
from django.http import HttpResponse

from .models import Article, Vendor


def article(request, slug):
    item = Article.objects.get(slug=slug)

    context = {'item': item}
    return render(request, 'pflops/article.html', context)


def vendors(request):
    items = Vendor.objects.all()

    context = {'items': items}
    return render(request, 'pflops/vendors.html', context)
