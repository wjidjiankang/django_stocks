from django.urls import path
from . import views


urlpatterns = [
 path('', views.index),
 path('buystock/',views.buystock,name='buystock'),
 path('trade/',views.trade, name='trade'),
 path('sellstock/',views.sellstock,name='sellstock')
]