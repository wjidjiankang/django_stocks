from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .forms import BuystockForm, SellstockForm, StockinhandForm
from .models import Record, StcokInHand, Profit, LowMarkerCap, Para, Partfolio300, Mydate,SVR
from datetime import datetime, date ,timedelta
from decimal import Decimal
import akshare as ak
import pandas as pd
import qstock as qs
# # import matplotlib.pyplot as plt
# from io import BytesIO
# import base64
# import imp
# import matplotlib
# from matplotlib import pyplot as plt
# import matplotlib.dates as mdates


def index(request):
    # 市值在20亿附近的股票list
    low_market_cap_df = get_market_cap()
    table = low_market_cap_df.to_html(index=False)

    # 组合还有多少现金
    cash_obj = Para.objects.filter(flag='lmup_cash').first()
    cash = cash_obj.value

    svr_obj = Para.objects.filter(flag='svr_cash').first()
    svr_cash = svr_obj.value


    # 一天只处理一次，实现天数的累积
    today = date.today()
    # before_day = today - timedelta(days=5)
    # print(before_day)
    data_today = Mydate.objects.filter(date=today).first()

    if data_today is None:
        new_data = Mydate(date=today)
        # 在这里添加你需要处理的数据
        # ...
        new_data.is_processed = True
        new_data.save()
        if is_trade(today):
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
            'svr_cash': svr_cash,
           }
    return render(request, 'index.html', dict)


# 判断是否是交易日
def is_trade(date):
    # 获取交易日期的信息
    tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
    if date in tool_trade_date_hist_sina_df['trade_date'].values:
        istrade = True
    else:
        istrade = False
    return istrade


# 根据code 获取股票的一些基本信息
def get_stock_information(code):
    stock = qs.realtime_data(code=code)
    name = stock['名称'].values[0]
    close = stock['最新'].values[0]
    ratio = stock['涨幅'].values[0]
    preclose = stock['昨收'].values[0]
    dict = {'name': name, 'close': close, 'ratio': ratio, 'preclose': preclose}
    return dict


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
                code = stock_form.data['code']
                stock = StcokInHand(code=code)
                stock.name = get_stock_information(code)['name']   # 根据股票code获取股票的名称
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
            # 小市值策略
            if strategy =='lmup':
                code = Para(flag='lmup_code', string=stock.code)
                code.save()
                cash = Para.objects.filter(flag='lmup_cash').first()
                print(cash)
                cash.value = cash.value - record.amount
                cash.save()

            # svr 支持向量机策略
            if strategy =='svr':
                code = Para(flag='svr_code', string=stock.code)
                code.save()
                cash = Para.objects.filter(flag='svr_cash').first()
                print(cash)
                cash.value = cash.value - record.amount
                cash.save()

            today = date.today()
            profit = Profit.objects.filter(date=today).first()

            profits = Profit.objects.all()
            len_profits = len(profits)
            pre_profit = profits[len_profits-2]
            cash_pre = pre_profit.cash

            if profit is None:
                profit = Profit(date=today)

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
            code = stock_form.data['code']
            stock = StcokInHand.objects.filter(code=code).first()
            stock.name = get_stock_information(code)['name']  # 股票的名称刷新
            stock.save()
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

            # svr 支持向量机 策略
            if strategy =='svr':
                code = Para.objects.filter(flag='svr_code', string=stock.code)
                code.delete()
                cash = Para.objects.filter(flag='svr_cash').first()
                cash.value = cash.value + record.amount
                cash.save()


            today = date.today()
            profit = Profit.objects.filter(date=today).first()

            profits = Profit.objects.all()
            len_profits = len(profits)
            pre_profit = profits[len_profits-2]
            cash_pre = pre_profit.cash

            if profit is None:
                profit = Profit(date=today)

            profit.cash_change = profit.cash_change + record.amount
            profit.cash = cash_pre + profit.cash_change
            profit.save()
    return redirect('stocks:trade')


# 刷新持有股票的数据
def refresh_stock():
    realtime_stock = ak.stock_zh_a_spot_em()   # 股票行情
    realtime_bond = ak.bond_zh_hs_cov_spot()  # 可转债行情
    realtime_etf = ak.fund_etf_spot_em()   # etf行情
    stocks = StcokInHand.objects.exclude(quantityinhand=0).all()
    # print(stocks[0].code)
    total_value = 0
    for stock in stocks:
        # print(stock.code)
        code = stock.code
        if code[0] in ['6','4','8','0','3']:   # 识别 股票
            stock_df = realtime_stock[realtime_stock['代码']==code]
            stock.name = stock_df['名称'].values[0]
            stock.close = Decimal(  stock_df['最新价'].values[0])
            stock.ratio = stock_df['涨跌幅'].values[0]
        elif code[0:2] in ['11','12']:  # 判断 可转债
            if code[0:2] == '11':      # 根据ak返回的数据结构,code + 'sh' 或'sz' 处理
                code  = 'sh'+ code
            else :
                code = 'sz'+ code
            stock_df = realtime_bond[realtime_bond['symbol']==code]
            stock.name = stock_df['name'].values[0]
            stock.close = Decimal(stock_df['trade'].values[0])
            stock.ratio = stock_df['pricechange'].values[0]
        else:                   # etf
            stock_df = realtime_etf[realtime_etf['代码'] == code]
            stock.name = stock_df['名称'].values[0]
            stock.close = Decimal(stock_df['最新价'].values[0])
            stock.ratio = stock_df['涨跌幅'].values[0]

        stock.save()
        total_value = stock.value + total_value

    today = date.today()
    profit = Profit.objects.filter(date=today).first()

    profits = Profit.objects.all()
    len_profits = len(profits)
    pre_profit = profits[len_profits - 2]
    cash_pre = pre_profit.cash
    total_pre = pre_profit.total

    if profit is None:
        profit = Profit(date=today)

    profit.cash = cash_pre + profit.cash_change
    profit.value = total_value
    profit.total = Decimal(profit.value) + profit.cash
    profit.profit = profit.total - total_pre
    profit.save()
    return profit



def stock_inhand(request):

    # total_value = 0
    # for stock in stocks:
    #     stock.save()
    #     total_value = stock.value + total_value
    #
    # today = date.today()
    # profit = Profit.objects.filter(date=today).first()
    #
    # profits = Profit.objects.all()
    # len_profits = len(profits)
    # pre_profit = profits[len_profits - 2]
    # cash_pre = pre_profit.cash
    # total_pre = pre_profit.total
    #
    # if profit is None:
    #     profit = Profit(date=today)
    #
    # profit.cash = cash_pre + profit.cash_change
    # profit.value = total_value
    # profit.total = Decimal(profit.value) + profit.cash
    # profit.profit = profit.total - total_pre
    # profit.save()
    profit = refresh_stock()
    stocks = StcokInHand.objects.exclude(quantityinhand=0).order_by('-ratio')

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
    profit = refresh_stock()
    profits = Profit.objects.all()
    make_lowmarket_cap_data()
    bench2lmcap = LowMarkerCap.objects.all()
    make_total_bench_data()
    bench2total = Partfolio300.objects.all()
    make_svr_data()
    bench2srv = SVR.objects.all()

    context={'profits': profits,
             'bench2lmcap': bench2lmcap,
             'bench2total': bench2total,
             'bench2svr': bench2srv,
             }

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
    ratio_300 = (close_300 / benchmark_300 - 1)*100

    # 策略里面股票的收盘价,市值
    values = 0
    lmup_stocks = Para.objects.filter(flag='lmup_code')
    for stock in lmup_stocks:
        code = stock.string
        obj = StcokInHand.objects.filter(code=code).first()
        values = values + obj.value
    total = values + cash
    value_ratio = (total / benchmark_total - 1)*100
    # print(value_ratio)

    today = date.today()
    # print(date)
    # print(type(date))

    # 数据存入数据库
    lmarketcap = LowMarkerCap.objects.filter(date=today).first()
    if lmarketcap is None:
        lmarketcap = LowMarkerCap(date=today)
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
    ratio_300 = (close_300/benchmark_300 -1)*100

    # 获取总资产的数据，从Profit表中
    today = date.today()
    # data_str = date.strftime('%Y-%m-%d')
    profit = Profit.objects.filter(date=today).first()
    if profit:
        total = profit.total
    else:
        total = 0
    total_ratio = (total/benchmark_total - 1)*100

    # 将数据写入数据库。如果没有记录，先创建一条记录（按照date)
    partfolio300 = Partfolio300.objects.filter(date=today).first()
    if partfolio300 is None:
        partfolio300 = Partfolio300(date=today)
    partfolio300.bench300 = close_300
    partfolio300.total = total
    partfolio300.bench_ratio = ratio_300
    partfolio300.total_ratio = total_ratio
    partfolio300.save()


# svr 策略的数据村进入数据库
def make_svr_data():
    benchmark_300 = 3692.89
    benchmark_total = 50000

    # 从数据库读取 cash
    cash_obj = Para.objects.filter(flag='svr_cash').first()
    # print(cash_obj.flag)
    cash = cash_obj.value

    # 获取沪深300的数据
    close_300 = get300index()
    ratio_300 = (close_300 / benchmark_300 - 1)*100

    # 策略里面股票的收盘价,市值
    # 这是考虑各个策略持股不同的情况。几个策略买了相同的股票，数据就会出错。下次需要改进
    values = 0
    svr_stocks = Para.objects.filter(flag='svr_code')
    for stock in svr_stocks:
        code = stock.string
        obj = StcokInHand.objects.filter(code=code).first()
        values = values + obj.value
    total = values + cash
    value_ratio = (total / benchmark_total - 1)*100
    # print(value_ratio)

    today = date.today()
    svr = SVR.objects.filter(date=today).first()
    if svr is None:
        svr = SVR(date=today)
    svr.bench300 = close_300
    svr.value = total
    svr.value_ratio = value_ratio
    svr.bench_ratio = ratio_300
    svr.save()


def cleandata(request):
    if request.method == "POST":
        profits = Profit.objects.filter(profit=0)
        for profit in profits:
            if not is_trade(profit.date):
                profit.delete()

        lowmarkets = LowMarkerCap.objects.all()
        for lowmarket in lowmarkets:
            if not is_trade(lowmarket.date):
                lowmarket.delete()

        partfolios = Partfolio300.objects.all()
        for partfolio in partfolios:
            if not is_trade(partfolio.date):
                partfolio.delete()
    return redirect('/profit/')

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