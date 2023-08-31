from django.db import models
import qstock as qs
from datetime import datetime
import akshare as ak

# Create your models here.


class StcokInHand(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=20)
    close = models.FloatField(default= 0 )
    ratio = models.FloatField(default= 0 )
    preclose = models.FloatField()
    buyquantity = models.IntegerField(default=0)
    buyamount = models.FloatField(default= 0 )
    sellquantity = models.IntegerField(default=0)
    sellamount = models.FloatField(default= 0 )
    quantityinhand = models.IntegerField()
    profit = models.FloatField(default= 0 ) #收益
    estimation = models.FloatField(default= 0 )  #估值
    value = models.FloatField(default=0)   #市值
    profit_day = models.FloatField(default=0)  # 当日收益
    profit_ratio = models.FloatField(default=0,blank=True, null=True)

    # def __init__(self, code):
    #     self.code = code

    def get_stock_inform(self):
        stock = qs.realtime_data(code=self.code)
        name = stock['名称'].values[0]
        close = stock['最新'].values[0]
        ratio = stock['涨幅'].values[0]
        preclose = stock['昨收'].values[0]
        dict = {'name': name, 'close': close, 'ratio': ratio, 'preclose': preclose}
        return dict

    # def get_profit_ratio(self):
    #     ratio = self.profit
    def get_estimation(self):
        estimation = 0
        try:
            stock_profit_forecast_ths_df = ak.stock_profit_forecast_ths(symbol=self.code, indicator="预测年报每股收益")
            n = len(stock_profit_forecast_ths_df)
            if n>=2:
                v2 = stock_profit_forecast_ths_df.iloc[n - 1]['均值']
                v1 = stock_profit_forecast_ths_df.iloc[n - 2]['均值']
                estimation = v1 * (v2 / v1 - 1) * 100
            else:
                estimation = 0
        except :
            estimation = 0
        return estimation


    def save(self, *args, **kargs):
        stockinform = self.get_stock_inform()
        # self.code = stockinform['code']
        self.name = stockinform['name']
        self.close = stockinform['close']
        self.ratio = stockinform['ratio']
        self.preclose = stockinform['preclose']
        self.quantityinhand = self.buyquantity - self.sellquantity
        self.profit = round((self.close * self.quantityinhand + float(self.sellamount) - float(self.buyamount)), 3)
        self.value = round((self.quantityinhand * self.close),3)
        self.profit_day = round((self.close-self.preclose)*self.quantityinhand, 3)
        self.profit_ratio = round((100*self.profit/self.buyamount), 3)
        self.estimation = round(self.get_estimation(),2)
        super(StcokInHand, self).save(*args, **kargs)

    def __str__(self):
        return self.name


class Record(models.Model):
    id = models.AutoField(primary_key=True)
    stock = models.ForeignKey(StcokInHand, on_delete=models.CASCADE,related_name='stock_code',null=True, blank=True, default=None)
    mark = models.CharField(max_length=4)
    quantity = models.IntegerField(default=0)
    price = models.FloatField(default= 0 )
    # tradefee = models.DecimalField(max_digits=11, decimal_places=3)
    amount = models.FloatField(default= 0 )
    date = models.CharField(max_length=10)

    def __str__(self):
        return self.stock

    def get_stock_cost(self):
        if self.quantity == 0:
            cost = self.price   # 分红的状况 ，以买入0股来表示
        else:
            cost = self.price * self.quantity
        cost = round(cost, 3)
        return cost

    def get_commission(self):  #佣金
        ratio = 2/10000
        stock_cost = self.get_stock_cost()
        kzz = self.stock.code[0]=='1' and (self.stock.code[1] == '1' or '2')
        commission = float(stock_cost) * float(ratio)
        if  commission < 5 and (not kzz):
            commission = 5
        commission = round(commission, 3)
        return commission

    def get_transfer_fee(self):
        ratio = 0.01/1000
        stock_cost = self.get_stock_cost()
        if self.stock.code[0] == '6':
            transfer_fee = float(stock_cost) * float(ratio)
        else:
            transfer_fee = 0
        transfer_fee = round(transfer_fee, 3)
        return transfer_fee

    def get_stamp_tax(self):
        ratio = 1/1000
        stock_cost = self.get_stock_cost()
        stamp_tax = float(stock_cost) * float(ratio)
        stamp_tax = round(stamp_tax, 3)
        return stamp_tax

    def get_ammount(self):
        stock_cost = float(self.get_stock_cost())
        commission = self.get_commission()
        stamp_tax = self.get_stamp_tax()
        transfer_fee = self.get_transfer_fee()
        if self.mark == 'buy':
            ammount = stock_cost + (commission + transfer_fee)
        if self.mark == 'sell':
            if self.stock.code[0] == '1' or '5':    #卖的时候收,可转债，ETF不收印花税
                ammount = stock_cost - (commission + transfer_fee)
            else:
                ammount = stock_cost -(commission + transfer_fee + stamp_tax)
        ammount = round(ammount,3)
        return ammount

    def save(self, *args, **kargs):
        self.amount = self.get_ammount()
        self.date = datetime.now().strftime('%Y-%m-%d')
        super(Record, self).save(*args, **kargs)

class Profit(models.Model):
    date = models.CharField(max_length=10)
    value = models.FloatField(default=0)
    buyamount = models.FloatField(default=0)
    sellamount = models.FloatField(default=0)
    total = models.FloatField(default=0)
    pre_total = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    cash = models.FloatField(default=0)
    pre_cash = models.FloatField(default=0)
    cash_change = models.FloatField(default=0)

    def save(self, *args, **kargs):
        self.date = datetime.now().strftime('%Y-%m-%d')
        # self.total = round((self.value + self.cash), 3)
        # self.profit = round((self.total - self.pre_total), 3)
        super(Profit, self).save(*args, **kargs)



