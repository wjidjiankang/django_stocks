from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from .forms import BuystockForm,SellstockForm,StockinhandForm
from .models import Record,StcokInHand,Profit
from datetime import datetime
# from .myinfom import profit_init,MyStock

# Create your views here.

def index(request):
    # return HttpResponse('hello')
    dict = {'name':'peter'}
    return render(request, 'index.html', dict)



def buystock(request):
    sell_form = SellstockForm()
    # if request.method=="GET":
    stock_form = StockinhandForm()
    buy_form = BuystockForm()
        # return render(request, 'trade.html', {'stock_form': stock_form,'buy_form':buy_form})
    if request.method=="POST":
        stock_form =StockinhandForm(request.POST)
        buy_form = BuystockForm(request.POST)
        print('1')
        if stock_form.is_valid() and buy_form.is_valid():
            print("2")
            stock = StcokInHand.objects.filter(code = stock_form.data['code']).first()
            print("3")
            print('4')
            if stock is None:
                print(stock_form.data['code'])
                stock = StcokInHand(code = stock_form.data['code'])
                stock.save()

            record = buy_form.save(commit=False)
            record.stock = stock
            record.mark='buy'
            record.save()

            stock.buyquantity = float(stock.buyquantity) + float(record.quantity)
            stock.buyamount = float(stock.buyamount) + float(record.amount)
            stock.save()

            date = datetime.now().strftime('%Y-%m-%d')
            profit = Profit.objects.filter(date= date).first()
            pre_profit = Profit.objects.last()
            if profit is None:
                profit  = Profit(date=date,pre_total=pre_profit.total,pre_cash=pre_profit.cash)

            profit.buyamount = profit.buyamount + record.amount
            profit.cash = round((profit.pre_cash + profit.sellamount - profit.buyamount), 3)
            # profit_init()
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
               'records':records
               }
    return render(request, 'trade.html', content)



def sellstock(request):
    stock_form = StockinhandForm()
    buy_form = BuystockForm()
    sell_form = SellstockForm()

        # return render(request, 'trade.html', content)
    if request.method == "POST":

        stock_form = StockinhandForm(request.POST)
        sell_form = SellstockForm(request.POST)
        if stock_form.is_valid() and sell_form.is_valid():
            stock = StcokInHand.objects.filter(code=stock_form.data['code']).first()
            record = sell_form.save(commit=False)
            record.stock = stock
            record.mark = 'sell'
            record.save()

            stock.sellquantity = stock.sellquantity + record.quantity
            stock.sellamount = stock.sellamount + record.amount
            stock.save()

            date = datetime.now().strftime('%Y-%m-%d')
            profit = Profit.objects.filter(date=date).first()
            pre_profit = Profit.objects.last()
            if profit is None:
                profit = Profit(date=date,pre_total=pre_profit.total,pre_cash=pre_profit.cash)
            # profit_init()
            profit.sellamount = profit.sellamount + record.amount
            profit.cash = round((profit.pre_cash + profit.sellamount - profit.buyamount), 3)
            profit.save()
    return redirect('stocks:trade')


def stock_inhand(request):
    stocks = StcokInHand.objects.exclude(quantityinhand = 0).order_by('-ratio')

    total_value = 0
    for stock in stocks:
        stock.save()
        total_value = stock.value + total_value

    date = datetime.now().strftime('%Y-%m-%d')
    profit = Profit.objects.filter(date=date).first()
    pre_profit = Profit.objects.last()
    if profit is None:
        profit = Profit(date=date, pre_total=pre_profit.total,pre_cash=pre_profit.cash)

    profit.cash = round((profit.pre_cash + profit.sellamount - profit.buyamount),3)
    # profit_init()
    profit.value = total_value
    profit.save()

    return render(request,'stockinhand.html',{'stocks':stocks,'profit':profit})


def stockdetail(request,code):
    stock = get_object_or_404(StcokInHand, code=code)
    records = Record.objects.filter(stock=stock)
    fullcode = ''
    if stock.code[0]=='6' or stock.code[0]=='5':
        fullcode = 'sh' + stock.code
    elif stock.code[0] == '0' or stock.code[0] == '1' or stock.code[0] == '3':
        fullcode = 'sz' + stock.code

    # mystock = MyStock(stock.code)
    # predict = 0
    # try:
    #     predict = mystock.cal_predict()
    # except:
    #     return HttpResponse("Can not predict the price of the stock!")
    # stock.estimation = predict
    # stock.save()

    content = {
             'stock':stock,
             'records':records,
             'fullcode':fullcode
             }
    return render(request,'stockdetail.html',content)



def profit(request):
    objs = Profit.objects.all()

    return render(request,'profit.html',locals())


def total(request):
    objs = Profit.objects.all()
    n = len(objs)
    last_profit = objs[n-1]
    # last_profitn = len()
    total = last_profit.total
    return HttpResponse('total is {}'.format(total))








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