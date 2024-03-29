"""anodos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
import anodos.views
import pflops.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('distributors/', include('distributors.urls')),

    path('login/', anodos.views.view_login),

    path('ajax/login/', anodos.views.ajax_login),
    path('ajax/logout/', anodos.views.ajax_logout),

    path('', pflops.views.view_index),
    path('search/', pflops.views.view_search),
    path('product/<slug:product_slug>/', pflops.views.view_product),

    path('catalog/<path:path>/', pflops.views.view_catalog_element),
    path('assistant/<path:path>/', pflops.views.view_assistant_element),

    path('ajax/get-parties/', pflops.views.ajax_get_parties),
    path('ajax/save-conversion-call/', pflops.views.ajax_save_conversion_call),
    path('ajax/load-catalog-element-image/', pflops.views.ajax_load_catalog_element_image),
    path('ajax/save-new-catalog-element/', pflops.views.ajax_save_new_catalog_element),
    path('ajax/load-assistant-element-image/', pflops.views.ajax_load_assistant_element_image),
    path('ajax/save-new-assistant-element/', pflops.views.ajax_save_new_assistant_element),
    path('ajax/product-image-upload/', pflops.views.ajax_product_image_upload),
    path('ajax/product-image-link/', pflops.views.ajax_product_image_link),

    path('<slug:slug>/', pflops.views.article),
]
