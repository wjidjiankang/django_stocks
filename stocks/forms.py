from django.forms import Form,ModelForm
from django import forms
from .models import Record, StcokInHand


class StockinhandForm(ModelForm):
    code = forms.CharField(max_length=6, min_length=6, required=True)

    class Meta:
        model = StcokInHand
        fields = ('code',)


class BuystockForm(ModelForm):
    price = forms.DecimalField()
    quantity = forms.IntegerField()

    class Meta:
        model = Record
        fields = ('price', 'quantity')




class SellstockForm(ModelForm):
    price = forms.DecimalField()
    quantity = forms.IntegerField()

    class Meta:
        model = Record
        fields = ('price', 'quantity' )




# class UserForm(ModelForm):
#     name = forms.CharField()
#     age = forms.IntegerField()
#
#     class Meta:
#         model = MyUser
#         fields = ('name','age')

    # class Meta:
    #     model = MyUser
    #     fields = ('name','age')
