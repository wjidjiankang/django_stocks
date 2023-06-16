"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('stocks/', include('stocks.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.urls import re_path
from stocks import views
# from previews.Stock import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stocks.urls',namespace='stocks')),
    # re_path(r'^$', views.index),
    # re_path(r'^data_entry/$', views.data_entry, name='data_entry'),
    # re_path(r'^add_fund_manger/$', views.add_fund_manger),
    # re_path(r'^add_stock/$', views.add_stock),
    # re_path(r'^check$', views.check_index, name='check'),
    # re_path(r'^trading/$', views.check),
    # re_path(r'^trading_success/$', views.trading),
    # re_path(r'^fund_pool/$', views.Fund_pool_, name='fund_pool'),
    # re_path(r'^account/$', views.Account)
]