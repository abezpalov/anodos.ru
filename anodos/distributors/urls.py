from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('product/<uuid:product_id>/', views.product),
    path('vendors/', views.vendors),

    path('ajax/do-vendor-as-is/', views.ajax_vendor_as_is),
    path('ajax/erase-vendor-link/', views.ajax_erase_vendor_link),


]
