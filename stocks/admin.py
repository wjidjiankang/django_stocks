from django.contrib import admin

# Register your models here.

from .models import StcokInHand, Record,Profit

admin.site.register(StcokInHand)
admin.site.register(Record)
admin.site.register(Profit)
