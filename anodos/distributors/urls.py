from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('product/stocks-<slug:distributor>/vendor-<slug:vendor>/article-<slug:article>',
         views.product)
]
