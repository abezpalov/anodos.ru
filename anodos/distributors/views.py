from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

from .models import Distributor, Product, Party, ParameterValue, ProductImage


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
            parties = Party.objects.filter(q)
            context = {
                'search': search,
                'parties': parties,
            }

    return render(request, 'distributors/search.html', context)


def product(request, product_id):

    item = Product.objects.get(id=product_id)

    params = ParameterValue.objects.filter(product=item)
    images = ProductImage.objects.filter(product=item)

    context = {'product': item, 'params': params, 'images': images}

    return render(request, 'distributors/product.html', context)


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
