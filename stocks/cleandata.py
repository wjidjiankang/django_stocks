import pandas as pd
import datetime
from models import Profit,LowMarkerCap,Partfolio300
from views import is_trade
import sqlite3

delete_profit = '''DELETE FROM profit WHERE profit = 0 '''
delete_lowmarketcap= '''DELETE FROM lowmarkercap WHERE profit = 0 '''


if __name__ =="__main__":
    conn = sqlite3.connect('StockDB.db')
    date = datetime.date.today()