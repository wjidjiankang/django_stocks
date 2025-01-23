import sqlite3
# import pandas as pd  # 导入pandas库
# from sqlalchemy import create_engine, Column, Integer, String, text, Float
# from sqlalchemy.orm import sessionmaker, declarative_base  # 导入orm模块的sessionmaker方法 ， # 映射基类，做数据库表和python类的映射关系
import akshare as ak
import datetime
import qstock as qs
from decimal import Decimal
import time

# sqlalchemy 初始设置
# Base = declarative_base()
# engine = create_engine('sqlite:///stockDB.db')
# Session = sessionmaker(bind=engine)
# session = Session()


# 直连sqlite3 设置
conn = sqlite3.connect(database='stockDB.db')
# cursor = conn.cursor()

# now = datetime.datetime.now()
# start_time = datetime.datetime(now.year,now.month, now.day, 9)
# print(now,start_time)


def get_stock_infrom(code):
    stock = qs.realtime_data(code=code)
    name = stock['名称'].values[0]
    close = stock['最新'].values[0]
    ratio = stock['涨幅'].values[0]
    preclose = stock['昨收'].values[0]
    dict = {'name': name, 'close': close, 'ratio': ratio, 'preclose': preclose}
    return dict


def get_estimation(code):
    estimation = 0
    try:
        stock_profit_forecast_ths_df = ak.stock_profit_forecast_ths(symbol=code, indicator="预测年报每股收益")
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


# 将实时数据定时写入数据库，
def write_real_data():
    while True:
        # 确定需要写入的时间
        today = datetime.date.today()
        now = datetime.datetime.now()
        start_time = datetime.time(9, 20)
        end_time = datetime.time(22, 30)

        tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
        if today in tool_trade_date_hist_sina_df['trade_date'].values:
            if start_time < now.time() < end_time:
                cursor = conn.cursor()
                query = " select code from stocks_stcokinhand where quantityinhand>0"
                codelist = cursor.execute(query).fetchall()
                # print(codelist)
                for code in codelist:
                    code = code[0]
                    stockinform = get_stock_infrom(code)
                    name = stockinform['name']
                    close = stockinform['close']
                    # close = Decimal(close_temp).quantize(Decimal('0.000'))
                    ratio = stockinform['ratio']
                    preclose = stockinform['preclose']
                    # preclose = Decimal(preclose_temp).quantize(Decimal('0.000'))

                    query = " update stocks_stcokinhand set name=? ,close=? ,ratio=? , preclose= ? where code =? "
                    cursor.execute(query, (name, close, ratio, preclose, code,))
                    conn.commit()

                    # print(preclose)
                    # print(type(preclose))
                    # print(type(code))
                    # print(type(name))
                    # print(type(close))
                    # print(type(ratio))
                    # print(code,close,ratio,preclose,name)
                cursor.close()
                print('更新完数据1次数据')

            else:
                print('非交易时间')
        else:
            print('非交易日期')
        time.sleep(180)


if __name__ == "__main__":
    write_real_data()
