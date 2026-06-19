import tushare as ts

ts.set_token("46cd2dce6fce352638b4896a90e61a1d7cb69cfe9c63bb90ed823b08")

pro = ts.pro_api()

df = pro.stock_basic(list_status='L')

print("数据行数:", len(df))
print(df.head())
