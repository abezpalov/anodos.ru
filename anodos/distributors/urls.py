from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('product/<uuid:product_id>/', views.view_product),
    path('vendors/', views.view_vendors),

    path('ajax/do-vendor-as-is/', views.ajax_vendor_as_is),
    path('ajax/erase-vendor-link/', views.ajax_erase_vendor_link),
    path('ajax/link-vendor/', views.ajax_link_vendor),
    path('ajax/save-vendor/', views.ajax_save_vendor),

]
