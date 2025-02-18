import pandas as pd
from typing import Optional
import requests

def get_stock_all_a_dc(page_count: Optional[int] = None,
                       proxies: Optional[dict] = {}) -> pd.DataFrame:
    """
    东方财富网-沪深京 A 股-实时行情
    https://quote.eastmoney.com/center/gridlist.html#hs_a_board
    :return: 实时行情
    :rtype: pandas.DataFrame
        1、序号:RANK
        2、代码:TS_CODE
        3、名称:NAME
        4、最新价:PRICE
        5、涨跌幅:PCT_CHANGE
        6、涨跌额:CHANGE
        7、成交量:VOLUME
        8、成交额:AMOUNT
        9、振幅:SWING
        10、最高:HIGH
        11、最低:LOW
        12、今开:OPEN
        13、昨收:CLOSE
        14、量比:VOL_RATIO
        15、换手率:TURNOVER_RATE
        16、市盈率-动态:PE
        17、市净率:PB
        18、总市值:TOTAL_MV
        19、流通市值:FLOAT_MV
        20、涨速:RISE
        21、5分钟涨跌:5MIN
        22、60日涨跌幅:60DAY
        23、年初至今涨跌幅:1YEAR
    """
    dfs = []
    for page in range(1,500):
        url = "http://82.push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": page,
            "pz": "200",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
            "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
            "_": "1623833739532",
        }
        if page_count:
            params["pz"] = 20
        r = requests.get(url, params=params, proxies=proxies)
        data_json = r.json()
        if not data_json["data"]:
            break
            # return pd.DataFrame()
        temp_df = pd.DataFrame(data_json["data"]["diff"])
        temp_df.columns = [
            "_",
            "最新价",
            "涨跌幅",
            "涨跌额",
            "成交量",
            "成交额",
            "振幅",
            "换手率",
            "市盈率-动态",
            "量比",
            "5分钟涨跌",
            "代码",
            "_",
            "名称",
            "最高",
            "最低",
            "今开",
            "昨收",
            "总市值",
            "流通市值",
            "涨速",
            "市净率",
            "60日涨跌幅",
            "年初至今涨跌幅",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
        ]
        temp_df.reset_index(inplace=True)
        # temp_df["index"] = temp_df.index + 1
        # temp_df.rename(columns={"index": "序号"}, inplace=True)
        temp_df = temp_df[
            [
                # "序号",
                "代码",
                "名称",
                "最新价",
                "涨跌幅",
                "涨跌额",
                "成交量",
                "成交额",
                "振幅",
                "最高",
                "最低",
                "今开",
                "昨收",
                "量比",
                "换手率",
                "市盈率-动态",
                "市净率",
                "总市值",
                "流通市值",
                "涨速",
                "5分钟涨跌",
                "60日涨跌幅",
                "年初至今涨跌幅",
            ]
        ]

        # temp_df["代码"] = temp_df["代码"].apply(format_stock_code)
        temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
        temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
        temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"], errors="coerce")
        temp_df["成交量"] = pd.to_numeric(temp_df["成交量"], errors="coerce")
        temp_df["成交额"] = pd.to_numeric(temp_df["成交额"], errors="coerce")
        temp_df["振幅"] = pd.to_numeric(temp_df["振幅"], errors="coerce")
        temp_df["最高"] = pd.to_numeric(temp_df["最高"], errors="coerce")
        temp_df["最低"] = pd.to_numeric(temp_df["最低"], errors="coerce")
        temp_df["今开"] = pd.to_numeric(temp_df["今开"], errors="coerce")
        temp_df["昨收"] = pd.to_numeric(temp_df["昨收"], errors="coerce")
        temp_df["量比"] = pd.to_numeric(temp_df["量比"], errors="coerce")
        temp_df["换手率"] = pd.to_numeric(temp_df["换手率"], errors="coerce")
        temp_df["市盈率-动态"] = pd.to_numeric(temp_df["市盈率-动态"], errors="coerce")
        temp_df["市净率"] = pd.to_numeric(temp_df["市净率"], errors="coerce")
        temp_df["总市值"] = pd.to_numeric(temp_df["总市值"], errors="coerce")
        temp_df["流通市值"] = pd.to_numeric(temp_df["流通市值"], errors="coerce")
        temp_df["涨速"] = pd.to_numeric(temp_df["涨速"], errors="coerce")
        temp_df["5分钟涨跌"] = pd.to_numeric(temp_df["5分钟涨跌"], errors="coerce")
        temp_df["60日涨跌幅"] = pd.to_numeric(temp_df["60日涨跌幅"], errors="coerce")
        temp_df["年初至今涨跌幅"] = pd.to_numeric(temp_df["年初至今涨跌幅"], errors="coerce")
        # temp_df.columns = [
        #     # "RANK",
        #     "TS_CODE",
        #     "NAME",
        #     "CLOSE",
        #     "PCT_CHANGE",
        #     "CHANGE",
        #     "VOLUME",
        #     "AMOUNT",
        #     "SWING",
        #     "HIGH",
        #     "LOW",
        #     "OPEN",
        #     "PRE_CLOSE",
        #     "VOL_RATIO",
        #     "TURNOVER_RATE",
        #     "PE",
        #     "PB",
        #     "TOTAL_MV",
        #     "FLOAT_MV",
        #     "RISE",
        #     "5MIN",
        #     "60DAY",
        #     "1YEAR",
        # ]
        # # 指定要转换为 float 类型的列
        # cols_to_convert = ['CLOSE', 'PCT_CHANGE', 'CHANGE', "VOLUME", "AMOUNT", "SWING",
        #                    'HIGH', "LOW", "OPEN", "PRE_CLOSE", "VOL_RATIO", "TURNOVER_RATE", "PE", "PB", "TOTAL_MV", "FLOAT_MV",
        #                    "RISE", "5MIN", "60DAY", "1YEAR"
        #                    ]
        # 使用 to_numeric() 方法将指定的列转换为 float 类型，并将非数值类型的数据转换为 NaN
        # temp_df[cols_to_convert] = temp_df[cols_to_convert].apply(pd.to_numeric, errors='coerce')
        dfs.append(
            temp_df
        )
        if page_count:
            break
    result_df = pd.concat(dfs, ignore_index=True)
    # 使用 fillna() 方法将 NaN 值替换为 0
    df_filled = result_df.fillna(0)
    df_sorted = df_filled.sort_values(by='涨跌幅', ascending=False).reset_index(drop=True)
    return df_sorted


def get_stock_all_ggt_dc(page_count: Optional[int] = None,
                         proxies: Optional[dict] = {}) -> pd.DataFrame:
    dfs = []
    for page in range(1,500):
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": page,
            "pz": "200",
            "po": "1",
            "np": "1",
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "fltt": "1",
            'dect': "1",
            "invt": "2",
            "fid": "f3",
            # "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
            "fs": "b:MK0144",
            "fields": "f12,f14,f2,f17,f3,f4",
            "_": "1739882296689",
        }
        if page_count:
            params["pz"] = 20
        r = requests.get(url, params=params, proxies=proxies)
        data_json = r.json()
        if not data_json["data"]:
            break
            # return pd.DataFrame()
        temp_df = pd.DataFrame(data_json["data"]["diff"])
        # print(temp_df)
        temp_df.columns = [
            # "_",
            "最新价",
            "涨跌幅",
            "涨跌额",
            "代码",
            "名称",
            "今开",
        ]
        # print(temp_df)
        temp_df.reset_index(inplace=True)
        temp_df = temp_df[
            [
                # "序号",
                "代码",
                "名称",
                "今开",
                "最新价",
                "涨跌幅",
                "涨跌额",
            ]
        ]
        # print(temp_df)
        temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
        temp_df["最新价"] = temp_df["最新价"].apply(etf_price_change)
        temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
        temp_df["涨跌幅"] = temp_df["涨跌幅"].apply(etf_price_change)
        temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"], errors="coerce")
        temp_df["涨跌额"] = temp_df["涨跌额"].apply(etf_price_change)
        temp_df["今开"] = pd.to_numeric(temp_df["今开"], errors="coerce")
        temp_df["今开"] = temp_df["今开"].apply(etf_price_change)
        dfs.append(
            temp_df
        )
        if page_count:
            break
    result_df = pd.concat(dfs, ignore_index=True)
    # 使用 fillna() 方法将 NaN 值替换为 0
    df_filled = result_df.fillna(0)
    df_sorted = df_filled.sort_values(by='涨跌幅', ascending=False).reset_index(drop=True)
    # print(df_sorted)
    return df_sorted


def get_all_etf_dc(page_count: Optional[int] = None,
                         proxies: Optional[dict] = {}) -> pd.DataFrame:
    dfs = []
    for page in range(1, 500):
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": page,
            "pz": "200",
            "po": "1",
            "np": "1",
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "fltt": "1",
            'dect': "1",
            "invt": "2",
            "fid": "f3",
            # "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
            "fs": "b:MK0021,b:MK0022,b:MK0023,b:MK0024,b:MK0827",
            "fields": "f12,f14,f2,f17,f3,f4",
            "_": "1739882296689",
        }
        if page_count:
            params["pz"] = 20
        r = requests.get(url, params=params, proxies=proxies)
        data_json = r.json()
        if not data_json["data"]:
            break
            # return pd.DataFrame()
        temp_df = pd.DataFrame(data_json["data"]["diff"])
        # print(temp_df)
        temp_df.columns = [
            # "_",
            "最新价",
            "涨跌幅",
            "涨跌额",
            "代码",
            "名称",
            "今开",
        ]
        # print(temp_df)
        temp_df.reset_index(inplace=True)
        temp_df = temp_df[
            [
                # "序号",
                "代码",
                "名称",
                "今开",
                "最新价",
                "涨跌幅",
                "涨跌额",
            ]
        ]
        # print(temp_df)
        temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
        temp_df["最新价"] = temp_df["最新价"].apply(etf_price_change)
        temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
        temp_df["涨跌幅"] = temp_df["涨跌幅"].apply(etf_price_change)
        temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"], errors="coerce")
        temp_df["涨跌额"] = temp_df["涨跌额"].apply(etf_price_change)
        temp_df["今开"] = pd.to_numeric(temp_df["今开"], errors="coerce")
        temp_df["今开"] = temp_df["今开"].apply(etf_price_change)
        dfs.append(
            temp_df
        )
        if page_count:
            break
    result_df = pd.concat(dfs, ignore_index=True)
    # 使用 fillna() 方法将 NaN 值替换为 0
    df_filled = result_df.fillna(0)
    df_sorted = df_filled.sort_values(by='涨跌幅', ascending=False).reset_index(drop=True)
    # print(df_sorted)
    # print(df_sorted)
    return df_sorted

def etf_price_change(d):
    new_d = d/1000
    return new_d


def main():
    # df = get_stock_all_a_dc()
    # print(df)

    get_stock_all_ggt_dc()
    get_all_etf_dc()

if __name__ == '__main__':
    main()