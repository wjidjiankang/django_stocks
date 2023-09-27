from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .forms import BuystockForm, SellstockForm, StockinhandForm
from .models import Record, StcokInHand, Profit, LowMarkerCap, Para
from datetime import datetime
from decimal import Decimal
import akshare as ak
import pandas as pd
import qstock as qs
import matplotlib.pyplot  as plt
from io import BytesIO
import base64
import imp


def index(request):
    dict = {'name': 'peter',
           }
    return render(request, 'index.html', dict)


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

            date = datetime.now().strftime('%Y-%m-%d')
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

            date = datetime.now().strftime('%Y-%m-%d')
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

    date = datetime.now().strftime('%Y-%m-%d')
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
    objs = Profit.objects.all()

    return render(request, 'profit.html', locals())


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


def lowmarketcap(request):
    low_market_cap_df = get_market_cap()
    table = low_market_cap_df.to_html(index=False)
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
    stock_300 = qs.realtime_data(code='000300')
    close_300 = stock_300['最新'].values[0]
    ratio_300 = close_300/benchmark_300 -1

    # 策略里面股票的收盘价
    values = 0
    lmup_stocks = Para.objects.filter(flag='lmup_code')
    for stock in lmup_stocks:
        code = stock.string
        obj = StcokInHand.objects.filter(code=code).first()
        values = values + obj.value
    # strategy_stocks = StcokInHand.objects.filter(strategy='lmup')
    # values= 0
    # buyamount = 0
    # sellmount = 0
    # for stock in strategy_stocks:
    #     values = values + stock.value
    #     buyamount = buyamount + stock.buyamount
    #     sellmount = sellmount + stock.sellamount
    total = values + cash
    value_ratio = total/benchmark_total -1
    print(value_ratio)

    # date = datetime.now().strftime('%Y-%m-%d')
    date = datetime.today().date()
    print(date)
    # print(type(date))

    #数据存入数据库
    lmarketcap = LowMarkerCap.objects.filter(date=date).first()
    if lmarketcap is None:
        lmarketcap= LowMarkerCap(date=date)
    lmarketcap.bench300 = close_300
    lmarketcap.value = total
    lmarketcap.value_ratio = value_ratio
    lmarketcap.bench_ratio = ratio_300
    lmarketcap.save()

    # dates=[]
    # ratio_300s=[]
    # ratio_strategy=[]

    # objs = LowMarkerCap.objects.all()
    # for lmcap in lmarketcaps:
    #     dates.append(lmcap.date)
    #     ratio_300s.append(lmcap.bench300)
    #     ratio_strategy.append(lmcap.value)
    # print(dates)
    # print(ratio_strategy)

    # # # fig, ax = plt.subplots(111)
    # plt.plot(dates, ratio_300s,'r')
    # plt.plot(dates, ratio_strategy,'b')
    # # buffer = BytesIO()
    # # plt.savefig(buffer)
    # # plt.close()
    # # base64img = base64.b64encode(buffer.getvalue())
    # # img = 'data:image/png;base64,'+base64img.decode()
    # plt.savefig('my_plot.png', bbox_inches='tight', pad_inches=0)
    # plt.close()
    #
    # # with open('my_plot.png','rb') as file:
    # #     plot_data = file.read()
    #
    content = {'cash': cash,
               'table': table,
               'benvalue': benchmark_total,
               }
    return render(request, 'lowmarketcap.html', context=content)


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