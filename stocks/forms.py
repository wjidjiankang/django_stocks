from django.forms import Form,ModelForm,Select
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

    # CHOICES_radio = (
    #     ('buy', '买入'),
    #     ('send', '送股'),
    # )
    #
    # CHOICES_select = (
    #     ('1', ''),
    #     ('2', 'ttxs'),
    #     ('3', 'yyds'),
    # )
    # my_choice_radio = forms.ChoiceField(choices=CHOICES_radio, widget=forms.RadioSelect(attrs={'layout': 'horizontal'}),
    #                               initial='buy')
    # my_choice_select = forms.ChoiceField(choices=CHOICES_select, widget=Select())

    class Meta:
        model = Record
        fields = ('amount', 'quantity')




class SellstockForm(ModelForm):
    amount = forms.DecimalField()
    quantity = forms.IntegerField()

    # CHOICES = (
    #     ('sell', '卖出'),
    #     ('dive', '分红'),
    # )
    # my_choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs={'layout': 'horizontal'}),
    #                               initial='sell')

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
