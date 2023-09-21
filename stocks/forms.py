from django.forms import Form,ModelForm
from django import forms
from .models import Record, StcokInHand


class StockinhandForm(ModelForm):
    code = forms.CharField(max_length=6, min_length=6, required=True)

    class Meta:
        model = StcokInHand
        fields = ('code',)


class BuystockForm(ModelForm):
    amount = forms.DecimalField()
    quantity = forms.IntegerField()

    class Meta:
        model = Record
        fields = ('amount', 'quantity')




class SellstockForm(ModelForm):
    amount = forms.DecimalField()
    quantity = forms.IntegerField()

    class Meta:
        model = Record
        fields = ('amount', 'quantity' )




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
