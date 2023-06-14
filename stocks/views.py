from django.shortcuts import render,HttpResponse,redirect
from .forms import BuystockForm,SellstockForm,StockinhandForm
from .models import Record,StcokInHand,Profit
from datetime import datetime

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
            if profit is None:
                profit  = Profit(date=date)
            profit.buyamount = profit.buyamount + record.amount
            profit.save()

    return redirect('trade')
            # return HttpResponse('buy ok')


def trade(request):
    stock_form = StockinhandForm()
    buy_form = BuystockForm()
    sell_form = SellstockForm()
    records = Record.objects.order_by('-date')[:30]

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
            pre_profit = Profit.objects.all().last()
            if profit is None:
                profit = Profit(date=date,pre_total=pre_profit.total)
            profit.sellamount = profit.sellamount + record.amount
            profit.save()
    return redirect('trade')










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