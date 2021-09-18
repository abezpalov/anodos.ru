from django.shortcuts import render
from django.http import HttpResponse

from .models import Article


def article(request, slug):
    item = Article.objects.get(slug=slug)

    context = {'item': item}
    return render(request, 'pflops/article.html', context)
