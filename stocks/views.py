from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .forms import BuystockForm, SellstockForm, StockinhandForm
from .models import Record, StcokInHand, Profit, LowMarkerCap, Para, Partfolio300, Mydate
from datetime import datetime, date ,timedelta
from decimal import Decimal
import akshare as ak
import pandas as pd
import qstock as qs
# import matplotlib.pyplot as plt
from io import BytesIO
import base64
import imp
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

date = date.today()

def index(request):
    #获取交易日期的信息
    import akshare as ak
    tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
    # print(tool_trade_date_hist_sina_df)
    # date = tool_trade_date_hist_sina_df.iloc[0, 0]
    # print(date)
    # print(type(date))
    # today = datetime.today().date()
    # print(today)

    # 市值在20亿附近的股票list
    low_market_cap_df = get_market_cap()
    table = low_market_cap_df.to_html(index=False)

    # 组合还有多少现金
    cash_obj = Para.objects.filter(flag='lmup_cash').first()
    cash = cash_obj.value

    # 一天只处理一次，实现天数的累积
    # today = date.today()
    # before_day = today - timedelta(days=5)
    # print(before_day)
    data_today = Mydate.objects.filter(date=date).first()

    if data_today is None:
        new_data = Mydate(date=date)
        # 在这里添加你需要处理的数据
        # ...
        new_data.is_processed = True
        new_data.save()
        if is_trade(date):
            print('a')
            para = Para.objects.filter(flag='lmup_date').first()
            para.value = para.value + 1
            para.save()
        # elif before_day in tool_trade_date_hist_sina_df['trade_date'].values:
        #     print('b')
    else:
        pass

    # 判断是否可以调仓
    para = Para.objects.filter(flag='lmup_date').first()
    days = para.value
    if days % 10 == 0 :
        low_market_tip = 'LMCAP 可以换以一下了'
    else:
        low_market_tip = 'LMCAP 再等等'

    # 东财股票热度
    hot_rank_em_df = ak.stock_hot_rank_em()[:20]
    hot_rank_em_df_html = hot_rank_em_df.to_html(index=False)

    # 东财热度飙升榜

    hot_up_em_df = ak.stock_hot_up_em()[:20]
    hot_up_em_df_html = hot_up_em_df.to_html(index=False)

    dict = {'table': table,
            'cash': cash,
            'low_market_tip': low_market_tip,
            'hot_rank_em_df_html': hot_rank_em_df_html,
            'hot_up_em_df_html': hot_up_em_df_html,
           }
    return render(request, 'index.html', dict)

def is_trade(date):
    import akshare as ak
    tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
    if date in tool_trade_date_hist_sina_df['trade_date'].values:
        istrade = True
    else:
        istrade = False
    return istrade


def buystock(request):
    sell_form = SellstockForm()
    # if request.method=="GET":
    stock_form = StockinhandForm()
    buy_form = BuystockForm()

    if request.method == "POST":
        stock_form = StockinhandForm(request.POST)
        buy_form = BuystockForm(request.POST)
        mark = request.POST.get('buy_radio')
        strategy = request.POST.get('stategy')

        if stock_form.is_valid() and buy_form.is_valid():
            stock = StcokInHand.objects.filter(code=stock_form.data['code']).first()

            if stock is None:
                # print(stock_form.data['code'])
                stock = StcokInHand(code=stock_form.data['code'])
                stock.save()

            record = buy_form.save(commit=False)
            record.stock = stock
            record.price = record.amount / record.quantity
            record.mark = mark
            # print(record.price)
            # print(record.mark)
            record.save()

            stock.buyquantity = stock.buyquantity + record.quantity
            stock.buyamount = stock.buyamount + Decimal(record.amount)
            # stock.strategy = strategy
            # print(stock.strategy)
            stock.save()

            # 把策略的信息存入数据库
            if strategy =='lmup':
                code = Para(flag='lmup_code', string=stock.code)
                code.save()
                cash = Para.objects.filter(flag='lmup_cash').first()
                print(cash)
                cash.value = cash.value - record.amount
                cash.save()

            # date = date.today()
            profit = Profit.objects.filter(date=date).first()

            profits = Profit.objects.all()
            len_profits = len(profits)
            pre_profit = profits[len_profits-2]
            cash_pre = pre_profit.cash

            if profit is None:
                profit = Profit(date=date)

            profit.cash_change = profit.cash_change - record.amount
            profit.cash = cash_pre + profit.cash_change

            profit.save()

    return redirect('stocks:trade')
    # return HttpResponse('buy ok')


def trade(request):
    stock_form = StockinhandForm()
    buy_form = BuystockForm()
    sell_form = SellstockForm()
    records = Record.objects.order_by('-id')[:30]

    content = {'stock_form': stock_form,
               'buy_form': buy_form,
               'sell_form': sell_form,
               'records': records
               }
    return render(request, 'trade.html', content)


def sellstock(request):
    stock_form = StockinhandForm()
    buy_form = BuystockForm()
    sell_form = SellstockForm()

    if request.method == "POST":
        stock_form = StockinhandForm(request.POST)
        sell_form = SellstockForm(request.POST)
        mark = request.POST.get('sell_radio')
        strategy = request.POST.get('stategys')
        if stock_form.is_valid() and sell_form.is_valid():
            stock = StcokInHand.objects.filter(code=stock_form.data['code']).first()
            record = sell_form.save(commit=False)
            record.stock = stock
            record.mark = mark
            if mark == 'sell':
                record.price = record.amount / record.quantity
            elif mark == 'divi':
                record.price = 0
            record.save()

            stock.sellquantity = stock.sellquantity + record.quantity
            stock.sellamount = stock.sellamount + record.amount
            if stock.buyquantity == stock.sellquantity:
                stock.strategy =''
            stock.save()

            # 策略code删除，cash 更新
            if strategy =='lmup':
                code = Para.objects.filter(flag='lmup_code', string=stock.code)
                code.delete()
                cash = Para.objects.filter(flag='lmup_cash').first()
                cash.value = cash.value + record.amount
                cash.save()

            # date = date.today()
            profit = Profit.objects.filter(date=date).first()

            profits = Profit.objects.all()
            len_profits = len(profits)
            pre_profit = profits[len_profits-2]
            cash_pre = pre_profit.cash

            if profit is None:
                profit = Profit(date=date)

            profit.cash_change = profit.cash_change + record.amount
            profit.cash = cash_pre + profit.cash_change
            profit.save()
    return redirect('stocks:trade')


def stock_inhand(request):
    stocks = StcokInHand.objects.exclude(quantityinhand=0).order_by('-ratio')

    total_value = 0
    for stock in stocks:
        stock.save()
        total_value = stock.value + total_value

    # date = date.today()
    profit = Profit.objects.filter(date=date).first()

    profits = Profit.objects.all()
    len_profits = len(profits)
    pre_profit = profits[len_profits - 2]
    cash_pre = pre_profit.cash
    total_pre = pre_profit.total

    if profit is None:
        profit = Profit(date=date)

    profit.cash = cash_pre + profit.cash_change
    profit.value = total_value
    profit.total = Decimal(profit.value) + profit.cash
    profit.profit = profit.total - total_pre
    profit.save()

    return render(request, 'stockinhand.html', {'stocks': stocks, 'profit': profit})


def stockdetail(request, code):
    stock = get_object_or_404(StcokInHand, code=code)
    records = Record.objects.filter(stock=stock)
    fullcode = ''
    if stock.code[0] == '6' or stock.code[0] == '5':
        fullcode = 'sh' + stock.code
    elif stock.code[0] == '0' or stock.code[0] == '1' or stock.code[0] == '3':
        fullcode = 'sz' + stock.code

    content = {
             'stock': stock,
             'records': records,
             'fullcode': fullcode
             }
    return render(request, 'stockdetail.html', content)


def profit(request):
    profits = Profit.objects.all()
    make_lowmarket_cap_data()
    bench2lmcap = LowMarkerCap.objects.all()
    make_total_bench_data()
    bench2total = Partfolio300.objects.all()

    context={'profits': profits,
             'bench2lmcap': bench2lmcap,
             'bench2total': bench2total,}

    return render(request, 'profit.html', context)


def total(request):
    objs = Profit.objects.all()
    n = len(objs)
    last_profit = objs[n-1]
    # last_profitn = len()
    total = last_profit.total
    return HttpResponse('total is {}'.format(total))


def get_market_cap(marketup=2000000000):
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    stock_df = stock_zh_a_spot_em_df[['代码', '名称', '总市值']].sort_values('总市值')
    stock_df.rename(columns={'代码': 'code', '名称': 'name', '总市值': 'marketcap'}, inplace=True)
    market = stock_df[stock_df['marketcap'] > marketup]
    marketup = market.iloc[:10]
        # print(stock_df)
        # print(market)
        # print(marketup)
    return marketup


def get300index():
    stock_300 = qs.realtime_data(code='000300')
    close_300 = stock_300['最新'].values[0]
    return close_300


def make_lowmarket_cap_data():
    benchmark_300 = 3692.89
    benchmark_total = 15000
    # cash= 15000

    # 从数据库读取 cash
    cash_obj = Para.objects.filter(flag='lmup_cash').first()
    # print(cash_obj.flag)
    cash = cash_obj.value
    # with open('cash.txt','r') as f:
    #     data = f.readlines()
    # # print(data)
    # data = data[0].strip()
    # # print(data)
    # cash = int(data)
    # # print(cash)

    # 获取沪深300的数据
    close_300 = get300index()
    ratio_300 = close_300 / benchmark_300 - 1

    # 策略里面股票的收盘价,市值
    values = 0
    lmup_stocks = Para.objects.filter(flag='lmup_code')
    for stock in lmup_stocks:
        code = stock.string
        obj = StcokInHand.objects.filter(code=code).first()
        values = values + obj.value
    total = values + cash
    value_ratio = total / benchmark_total - 1
    # print(value_ratio)

    date = datetime.today().date()
    # print(date)
    # print(type(date))

    # 数据存入数据库
    lmarketcap = LowMarkerCap.objects.filter(date=date).first()
    if lmarketcap is None:
        lmarketcap = LowMarkerCap(date=date)
    lmarketcap.bench300 = close_300
    lmarketcap.value = total
    lmarketcap.value_ratio = value_ratio
    lmarketcap.bench_ratio = ratio_300
    lmarketcap.save()


def make_total_bench_data():
    benchmark_300 = 3692.89
    benchmark_total = 650907

    #获取沪深300的指数
    close_300 = get300index()
    ratio_300 = close_300/benchmark_300 -1

    # 获取总资产的数据，从Profit表中
    date = datetime.today().date()
    data_str = date.strftime('%Y-%m-%d')
    profit = Profit.objects.filter(date=data_str).first()
    if profit:
        total = profit.total
    else:
        total = 0
    total_ratio = total/benchmark_total - 1

    # 将数据写入数据库。如果没有记录，先创建一条记录（按照date)
    partfolio300 = Partfolio300.objects.filter(date=date).first()
    if partfolio300 is None:
        partfolio300 = Partfolio300(date=date)
    partfolio300.bench300 = close_300
    partfolio300.total = total
    partfolio300.bench_ratio = ratio_300
    partfolio300.total_ratio = total_ratio
    partfolio300.save()






# 原来通过这个模块，再使用matplotlib来绘制图案，在前端输出
# 后来的方案是使用echarts，所以不用了
# def lowmarketcap(request):
#
#     benchmark_300 = 3692.89
#     benchmark_total = 15000
#     # cash= 15000
#
#     # 从数据库读取 cash
#     cash_obj = Para.objects.filter(flag='lmup_cash').first()
#     # print(cash_obj.flag)
#     cash = cash_obj.value
#     # with open('cash.txt','r') as f:
#     #     data = f.readlines()
#     # # print(data)
#     # data = data[0].strip()
#     # # print(data)
#     # cash = int(data)
#     # # print(cash)
#
#     # 获取沪深300的数据
#     close_300 = get300index()
#     ratio_300 = close_300/benchmark_300 -1
#
#     # 策略里面股票的收盘价,市值
#     values = 0
#     lmup_stocks = Para.objects.filter(flag='lmup_code')
#     for stock in lmup_stocks:
#         code = stock.string
#         obj = StcokInHand.objects.filter(code=code).first()
#         values = values + obj.value
#     total = values + cash
#     value_ratio = total/benchmark_total -1
#     # print(value_ratio)
#
#     date = datetime.today().date()
#     # print(date)
#     # print(type(date))
#
#     #数据存入数据库
#     lmarketcap = LowMarkerCap.objects.filter(date=date).first()
#     if lmarketcap is None:
#         lmarketcap= LowMarkerCap(date=date)
#     lmarketcap.bench300 = close_300
#     lmarketcap.value = total
#     lmarketcap.value_ratio = value_ratio
#     lmarketcap.bench_ratio = ratio_300
#     lmarketcap.save()
#
#     # 画图
#     dates = []
#     benchs = []
#     strategys = []
#     returns = LowMarkerCap.objects.all()
#     for ret in returns:
#         dates.append(ret.date)
#         benchs.append(ret.bench_ratio)
#         strategys.append(ret.value_ratio)
#     # print(dates[0])
#
#     matplotlib.use('Agg')    #一定要这句。不然会报错
#     fig,ax = plt.subplots(figsize=(8, 4))
#     # fig = plt.figure(figsize=(9, 4))
#     # 画布边缘设置颜色
#     fig.patch.set_facecolor('white')
#     fig.patch.set_alpha(0.1)
#
#     ax.plot(dates,benchs, 'r', label='HS300',)
#     ax.plot(dates,strategys, 'b', label='Low Market Cap',)
#     ax.legend(loc='best')
#     plt.xlabel('Date')
#     total_len =len(dates)
#     interval = total_len // 10
#     ax.xaxis.set_major_locator(mdates.DayLocator(interval))
#
#     sio = BytesIO()
#     plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0, transparent=True)
#     data = base64.encodebytes(sio.getvalue()).decode()
#     img = 'data:image/png;base64,' + str(data)
#     # 记得关闭，不然画出来的图是重复的
#     plt.close()
#     # plt.show()
#
#     content = {'cash': cash,
#                'img': img,
#                'dates': dates,
#                'benchs':benchs,
#                'strategys': strategys,
#                'objs': returns
#                }
#     return render(request, 'lowmarketcap.html', context=content)


# 原来通过这个模块，再使用matplotlib来绘制图案，在前端输出
# 后来的方案是使用echarts，所以不用了
# def totalbench(request):
#     benchmark_300 = 3692.89
#     benchmark_total = 650907
#
#     #获取沪深300的指数
#     close_300 = get300index()
#     ratio_300 = close_300/benchmark_300 -1
#
#     # 获取总资产的数据，从Profit表中
#     date = datetime.today().date()
#     data_str = date.strftime('%Y-%m-%d')
#     profit = Profit.objects.filter(date=data_str).first()
#     if profit:
#         total = profit.total
#     else:
#         total = 0
#     total_ratio = total/benchmark_total - 1
#
#     # 将数据写入数据库。如果没有记录，先创建一条记录（按照date)
#     partfolio300 = Partfolio300.objects.filter(date=date).first()
#     if partfolio300 is None:
#         partfolio300 = Partfolio300(date=date)
#     partfolio300.bench300 = close_300
#     partfolio300.total = total
#     partfolio300.bench_ratio = ratio_300
#     partfolio300.total_ratio = total_ratio
#     partfolio300.save()
#
#     objs = Partfolio300.objects.all()
#     # print(objs)
#
#     # 画图的数据
# #     dates = []
# #     benchs = []
# #     totals = []
# #     returns = Partfolio300.objects.all()
# #     for ret in returns:
# #         dates.append(ret.date)
# #         benchs.append(ret.bench_ratio)
# #         totals.append(ret.total_ratio)
# #     print(totals[0])
# #
# #     #画图
# #     matplotlib.use('Agg')  # 一定要这句。不然会报错
# #     fig, ax = plt.subplots(figsize=(9, 4))
# #     # fig = plt.figure(figsize=(9, 4))
# #     # 画布边缘设置颜色
# #     fig.patch.set_facecolor('white')
# #     fig.patch.set_alpha(0.5)
# #
# #     ax.plot(dates, benchs, 'r', label='HS300')
# #     ax.plot(dates, totals, 'b', label='Property')
# #     ax.legend(loc='best')
# #     plt.xlabel('Date')
# #     total_len = len(dates)
# #     interval = total_len // 10
# #     ax.xaxis.set_major_locator(mdates.DayLocator(interval))
# #
# #     sio = BytesIO()
# #     plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
# #     data = base64.encodebytes(sio.getvalue()).decode()
# #     img = 'data:image/png;base64,' + str(data)
# #     # 记得关闭，不然画出来的图是重复的
# #     plt.close()
# #     # plt.show()
# #
# #     content = {
# #                'img': img,
# #                }
# #     x = [3,6,7]
# #     print(locals())
#     return render(request, 'totalbench.html', {'objs':objs})
#
#



    # if request.method =='POST':
    #     buy_form = BuystockForm(request.POST)
    #     stock_form = StockinhandForm(request.POST)
    #     if buy_form.is_valid() and stock_form.is_valid():
    #         stock = StcokInHand.objects.filter(code = stock_form.data).first()
    #         if stock is None:
    #             stock.code = stock_form.data
    #             # stock.save(commit=False)
    #         stock.price = stock.get_price()
    #         record = buy_form.data
    #         # record.save(commit=False)
    #         record.mark = 'buy'
    #         record.tradefee = record.get_tradefee()
    #         record.amount = record.get_amount()
    #         stock.buyquantity = stock.buyquantity+record.quantity
    #         stock.buyamount = stock.buyamount+record.quantity
    #         stock.save()
    #         record.save()
    #         return HttpResponse('save ok')


    # code = request.POST.get('bcode')
    # price = request.POST.get('bprice')
    # quantity = request.POST.get('bquantity')
    # mark = 'buy'
    #
    # stock = StcokInHand.objects.get(code)
    # if not stock:
    #     stock.code = code
    # stock.price = stock.get_price()
    #
    # record.price = price
    # record.quantity = quantity
    # record.mark = 'buy'
    # record.tradefee = record.get_tradefee()
    # record.amount = record.get_amount()
    #
    # stock.buyquantity = stock.buyquantity + record.quantity
    # stock.buyamount = stock.buyamount + record.quantity
    # stock.profit = stock.get_profit()
    # stock.save()
    # record.save()
    # return render(request, 'index.html', {'name': 'shen'})


  #
  #   bstock = models.Stock()
  #   mystock = models.StockInHand()
  #   # mystock_profit = models.StockProfitbyOp()
  #   if request.method == 'POST':
  #       mark = 'Buy'
  #       code = request.POST.get('bcode')
  #       # name = getname(code)
  #       # name = getstockname(code)
  #       quantity = float(request.POST.get('bquantity'))
  #       # amount = request.POST.get('bamount')
  #       price = float(request.POST.get('bprice'))
  #       # name = '比亚迪'
  #       buystock = myinform.StockTrade(symbol=code, quantity=quantity, mark=mark, price=price)
  #       bstock.code = buystock.code
  #       bstock.name = buystock.name
  #       bstock.quantity = buystock.quantity
  #       bstock.amount = buystock.ammount
  #       bstock.mark = mark
  #       bstock.price = price
  #       bstock.save()
  # stocks  = models.StockInHand.objects.filter(code =code)
  #   word = "买入成功"
  #   if stocks :
  #       mystock = stocks[0]
  #       mystock.quantity = mystock.quantity+ bstock.quantity
  #       mystock.amount = float(mystock.amount) + bstock.amount
  #   else:
  #       mystock.code = buystock.code
  #       mystock.name = buystock.name
  #       mystock.quantity = bstock.quantity
  #       mystock.amount = bstock.amount
  #       mystock.ratio = 0
  #   mystock.cost = mystock.amount / mystock.quantity
  #   mystock.save()
  #   # print (mystock.amount)
  #
  #   # stocks_profit = models.StockProfitbyOp.objects.filter(code =code)
  #   # if stocks_profit :
  #   #     mystock_profit = stocks_profit[0]
  #   #     mystock_profit.cost = (float(mystock_profit.cost)*float(mystock_profit.ttlquantity) + float(amount))/(float(mystock_profit.ttlquantity)+float(quantity))
  #   #     mystock_profit.ttlquantity = float(mystock_profit.ttlquantity)+float(quantity)
  #   # else:
  #   #     mystock_profit.code  = code
  #   #     mystock_profit.name = name
  #   #     mystock_profit.ttlquantity = bstock.quantity
  #   #     mystock_profit.cost = float(amount)/float(bstock.quantity)
  #   # mystock_profit.save()
  #
  #   list_obj = models.Stock.objects.order_by("id").reverse()
  #   user_list_obj = list_obj[:20]
  #   # user_list_obj = models.Fund.objects.filter(name ='比亚迪')
  #   # user_list_obj = models.Fund.objects.last()
  #   return render(request, 'data_entry.html', {'li': user_list_obj,'word':word})