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

    path('', anodos.views.view_index),
    path('login/', anodos.views.view_login),

    path('ajax/login/', anodos.views.ajax_login),
    path('ajax/logout/', anodos.views.ajax_logout),

    path('search/', pflops.views.view_search),
    path('product/<slug:product_slug>/', pflops.views.view_product),

    path('<slug:slug>/', pflops.views.article),
]
