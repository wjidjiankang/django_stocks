from django.urls import path,re_path
from . import views

app_name = 'stocks'

urlpatterns = [
 path('', views.index, name='index'),
 path('buystock/', views.buystock, name='buystock'),
 path('trade/', views.trade, name='trade'),
 path('sellstock/', views.sellstock, name='sellstock'),
 path('stockinhand/', views.stock_inhand, name='stockinhand'),
 # path('detail/(?P<code>)',views.stockdetail,name='stockdetail'),
 re_path(r'^detail/(?P<code>\d{5,6})/$', views.stockdetail, name='stockdetail'),
 path('profit/', views.profit, name='profit'),
 path('total/', views.total, name='total'),
 # path('lowmarketcap/', views.lowmarketcap, name='lowmarketcap'),
 # path('totalbench/', views.totalbench, name='totalbench'),
 # path('cleandata/', views.cleandata, name='cleandata'),
]