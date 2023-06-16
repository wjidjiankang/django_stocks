from .models import Profit
from datetime import datetime

def profit_init():
    date = datetime.now().strftime('%Y-%m-%d')
    profit = Profit.objects.filter(date=date).first()
    pre_profit = Profit.objects.last()
    if profit is None:
        profit = Profit(date=date, pre_total=pre_profit.total, pre_cash=pre_profit.cash)
    profit.cash = round((profit.pre_cash + profit.sellamount - profit.buyamount), 3)
    # profit.save()