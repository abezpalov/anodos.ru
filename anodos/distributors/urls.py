from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('product/<uuid:product_id>/', views.product),
]
