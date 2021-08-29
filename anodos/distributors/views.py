from django.shortcuts import render
from django.http import HttpResponse

from .models import Distributor


def index(request):
    distributors = Distributor.objects.all()
    context = {'distributors': distributors}
    return render(request, 'distributors/index.html', context)
