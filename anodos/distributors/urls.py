from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('product/<uuid:product_id>/', views.view_product),
    path('vendors/', views.view_vendors),
    path('categories/', views.view_categories),
    path('parameters/', views.view_parameters),

    path('ajax/do-vendor-as-is/', views.ajax_vendor_as_is),
    path('ajax/erase-vendor-link/', views.ajax_erase_vendor_link),
    path('ajax/link-vendor/', views.ajax_link_vendor),
    path('ajax/save-vendor/', views.ajax_save_vendor),

    path('ajax/do-parameter-as-is/', views.ajax_parameter_as_is),
    path('ajax/erase-parameter-link/', views.ajax_erase_parameter_link),
    path('ajax/link-parameter/', views.ajax_link_parameter),
    path('ajax/save-parameter/', views.ajax_save_parameter),

    path('ajax/do-unit-as-is/', views.ajax_unit_as_is),
    path('ajax/erase-unit-link/', views.ajax_erase_unit_link),
    path('ajax/link-unit/', views.ajax_link_unit),
    path('ajax/save-unit/', views.ajax_save_unit),

]
