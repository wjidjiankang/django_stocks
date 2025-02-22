from django.db import models
import qstock as qs
from datetime import datetime, date
import akshare as ak
from decimal import Decimal

# Create your models here.

class StcokInHand(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=20)
    close = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    ratio = models.FloatField(default=0)
    preclose = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    buyquantity = models.IntegerField(default=0)
    buyamount = models.DecimalField(max_digits=11, decimal_places=2, default=1)
    sellquantity = models.IntegerField(default=0)
    sellamount = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    quantityinhand = models.IntegerField()
    profit = models.DecimalField(max_digits=11, decimal_places=2, default=0)  # 收益
    estimation = models.DecimalField(max_digits=8, decimal_places=3, default=0)  # 估值
    value = models.DecimalField(max_digits=11, decimal_places=2, default=0)   # 市值
    profit_day = models.DecimalField(max_digits=11, decimal_places=2, default=0)  # 当日收益
    profit_ratio = models.FloatField(default=0, blank=True, null=True)
    strategy = models.CharField(max_length=20,default='2')

    # def get_stock_inform(self):
    #     stock = qs.realtime_data(code=self.code)
    #     name = stock['名称'].values[0]
    #     close = stock['最新'].values[0]
    #     ratio = stock['涨幅'].values[0]
    #     preclose = stock['昨收'].values[0]
    #     dict = {'name': name, 'close': close, 'ratio': ratio, 'preclose': preclose}
    #     return dict

    def get_estimation(self):
        estimation = 0
        try:
            stock_profit_forecast_ths_df = ak.stock_profit_forecast_ths(symbol=self.code, indicator="预测年报每股收益")
            n = len(stock_profit_forecast_ths_df)
            if n >= 2:
                v2 = stock_profit_forecast_ths_df.iloc[n - 1]['均值']
                v1 = stock_profit_forecast_ths_df.iloc[n - 2]['均值']
                estimation = v1 * (v2 / v1 - 1) * 100
            else:
                estimation = 0
        except:
            estimation = 0
        return Decimal(estimation)

    def save(self, *args, **kargs):
        # stockinform = self.get_stock_inform()
        # self.name = stockinform['name']
        # # self.close = stockinform['close']
        # close = stockinform['close']
        # self.close = Decimal(close).quantize(Decimal('0.000'))
        # self.ratio = stockinform['ratio']
        # preclose = stockinform['preclose']
        # self.preclose = Decimal(preclose).quantize(Decimal('0.000'))

        self.quantityinhand = self.buyquantity - self.sellquantity
        self.profit = round(self.close * self.quantityinhand + self.sellamount - self.buyamount, 2)
        self.value = round(self.quantityinhand * self.close, 2)
        # self.profit_day = round((self.close-self.preclose) * self.quantityinhand, 2)
        self.profit_ratio = 100*self.profit/self.buyamount
        # self.estimation = self.get_estimation()
        super(StcokInHand, self).save(*args, **kargs)

    def __str__(self):
        return self.name


class Record(models.Model):
    id = models.AutoField(primary_key=True)
    stock = models.ForeignKey(StcokInHand, on_delete=models.CASCADE, related_name='stock_code', null=True, blank=True, default=None)
    mark = models.CharField(max_length=4)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField()

    def __str__(self):
        return self.stock

    def get_stock_cost(self):
        if self.quantity == 0:
            cost = self.price   # 分红的状况 ，以买入0股来表示
        else:
            cost = self.price * self.quantity
        cost = round(cost, 2)

        return cost

    def get_commission(self):   # 佣金
        ratio = 2/10000
        stock_cost = self.get_stock_cost()
        kzz = self.stock.code[0] == '1' and (self.stock.code[1] == '1' or '2')
        commission = float(stock_cost) * float(ratio)
        if commission < 5 and (not kzz):
            commission = 5
        commission = round(commission, 2)

        return commission

    def get_transfer_fee(self):
        ratio = 0.01/1000
        stock_cost = self.get_stock_cost()

        if self.stock.code[0] == '6':
            transfer_fee = float(stock_cost) * float(ratio)
        else:
            transfer_fee = 0
        transfer_fee = round(transfer_fee, 2)

        return transfer_fee

    def get_stamp_tax(self):
        ratio = 1/1000
        stock_cost = self.get_stock_cost()
        stamp_tax = float(stock_cost) * float(ratio)
        stamp_tax = round(stamp_tax, 2)

        return stamp_tax

    def get_ammount(self):
        stock_cost = float(self.get_stock_cost())
        commission = self.get_commission()
        stamp_tax = self.get_stamp_tax()
        transfer_fee = self.get_transfer_fee()

        if self.mark == 'buy':
            ammount = stock_cost + (commission + transfer_fee)
        if self.mark == 'sell':
            if self.stock.code[0] == '1' or '5':    # 卖的时候收,可转债，ETF不收印花税
                ammount = stock_cost - (commission + transfer_fee)
            else:
                ammount = stock_cost - (commission + transfer_fee + stamp_tax)
        ammount = round(ammount, 2)

        return Decimal(ammount)

    def save(self, *args, **kargs):
        # self.amount = self.get_ammount()
        self.date = date.today()
        super(Record, self).save(*args, **kargs)


class Profit(models.Model):
    date = models.DateField()
    value = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    cash = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    cash_change = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    def save(self, *args, **kargs):
        self.date = date.today()
        super(Profit, self).save(*args, **kargs)

class LowMarkerCap(models.Model):
    date = models.DateField()
    bench300 = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    value = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    bench_ratio = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    value_ratio = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    # def get_bench300(self):
    #     stock = qs.realtime_data(code='000300')
    #     index =  stock['最新'].values[0]
    #     return index

class Partfolio300(models.Model):
    date = models.DateField()
    bench300 = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    bench_ratio = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    total_ratio = models.DecimalField(max_digits=11, decimal_places=2, default=0)


    # def save(self, *args, **kargs):
    #     self.bench300 = self.get_bench300()
    #     self.date = datetime.now().strftime('%Y-%m-%d')
    #     super(LowMarkerCap, self).save(*args, **kargs)

class Para(models.Model):
    flag = models.CharField(max_length=15)
    value = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    string = models.CharField(max_length=15)



class Mydate(models.Model):
    date = models.DateField()
    is_processed = models.BooleanField(default=False)


# 支持向量机 策略的数据
class SVR(models.Model):
    date = models.DateField()
    bench300 = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    value = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    bench_ratio = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    value_ratio = models.DecimalField(max_digits=11, decimal_places=2, default=0)
