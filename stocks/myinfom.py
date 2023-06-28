# from .models import Profit
# from models import Profit
from datetime import datetime
import akshare as ak
import pandas as pd
import numpy as np

# def profit_init():
#     date = datetime.now().strftime('%Y-%m-%d')
#     profit = Profit.objects.filter(date=date).first()
#     pre_profit = Profit.objects.last()
#     if profit is None:
#         profit = Profit(date=date, pre_total=pre_profit.total, pre_cash=pre_profit.cash)
#     profit.cash = round((profit.pre_cash + profit.sellamount - profit.buyamount), 3)
#     # profit.save()



class MyStock():
    def __init__(self,code):
        self.code = code

    def cal_predict(self):
        fore_eps_df = ak.stock_profit_forecast_ths(symbol=self.code, indicator="预测年报每股收益")
        print(fore_eps_df)
        fore_eps_list = []
        for i in range(3):
            fore_eps_list.append(fore_eps_df.iloc[i, 3])
        price_evaluate = fore_eps_list[2] * (fore_eps_list[2] / fore_eps_list[1] - 1) * 100  # 预估2年后的估值
        price_evaluate = round(price_evaluate, 2)  # 只保留2位小小数
        return price_evaluate

    def cal_estimation(self):
        stock_profit_forecast_em_df = ak.stock_profit_forecast_em()
        code = '600036'
        print(stock_profit_forecast_em_df)



testcode = '600036'
teststock = MyStock(testcode)
print(teststock.cal_predict())
teststock.cal_estimation()
print(teststock)
