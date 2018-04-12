import requests
import re
import json
import numpy as np
import pandas as pd
import time
import sys

with open('cookie.txt','rb') as f:
    cookie = str(f.readline())
    

def getHTMLText(url,headers):
    try:
        r = requests.get(url,headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.content
    except Exception as e:
        print(str(e))
        return ""
    

def getJSList(content):
    js = content.split(b'data:')[1][:-1]
    l = eval(js)
    l = np.array(l)
    return l


def getPageInfo():
    url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?\
type=ct&st=(BalFlowMain)&sr=-1&p=1&ps=100&js=var%20CyvdbAfK={pages:(pc),\
date:%222014-10-22%22,data:[(x)]}&token=894050c76af8597a853f5b408b759f5d&\
cmd=C._AB&sty=DCFFITA&rt=50752228'
    
    headers = {'Accept' : '*/*', 'Accpet-Encoding': 'zh-CN,zh;q=0.8',
               'Host': 'nufm.dfcfw.com',
               'Referer': 'http://data.eastmoney.com/zjlx/detail.html',
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/\
537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    
    r = getHTMLText(url,headers=headers)
    l = getJSList(r)
    df = list2Frame(l)
    return df

    
def getMyStock():
    headers = {'Accept' : '/*/',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'nufm.dfcfw.com',
               'Referer': 'http://quote.eastmoney.com/favor/default.html',
               'Cookie': cookie,
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/\
537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    stock_list_url = 'https://myfavor1.eastmoney.com/mystock?f=gs&\
cb=getStockInfo&g=1693130&0.8179450208622452'
    html = getHTMLText(stock_list_url,headers)
    d = eval(html.split(b'"data":')[1][:-3])
    l = d['order'].split(',')
    result = []
    if l == ['']:
        return result
    for v in l:
        result.append(v[:6]+v[8])
    return result


def add2MyStock(code):
    headers = {'Accept' : '/*/',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'mystock.eastmoney.com',
               'Referer': 'http://data.eastmoney.com/stockdata/%s.html' % code[:6],
               'Cookie': cookie,
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/\
537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    
    url = 'http://mystock.eastmoney.com/mystock.aspx?f=asz&sc=%s&\
var=opfavres&rt=1207' % code
    html = getHTMLText(url, headers)


def getProfit(code):
    url = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?\
id=%s&token=beb0a0047196124721f56b0f0ff5a27c&\
cb=callback07919512506254929\
&callback=callback07919512506254929&_=1522893826640'%code
    headers = {'Accept' : 'text/html,application/xhtml+xml,\
application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'data.eastmoney.com',
               'Referer': 'http://data.eastmoney.com/zjlx/detail.html',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/\
537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    html = getHTMLText(url,headers)
    profit = eval(html.split(b'Value":')[1][:-2])[38]
    return profit


def isHighThanPre(code, flag):
    url = 'http://data.eastmoney.com/DataCenter_V3/stockdata/cwzy.ashx?code=%s.SH'%code
    headers = {'Accept' : 'text/html,application/xhtml+xml,application/\
xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'data.eastmoney.com',
               'Referer': 'http://data.eastmoney.com/zjlx/detail.html',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/\
537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    html = getHTMLText(url,headers)
    l = eval(html)
    if l == []:
        return isHighThanPre0(code, flag)
    price0 = l[0]['BasicEPS']
    price1 = l[-1]['BasicEPS']
    if price0 == '' or price1 == '':
        return True
    return float(price0) > float(price1)
    

def isHighThanPre0(code, flag):
    f = {'1': 'sh', '2': 'sz'}
    code = f[flag] + code
    url = 'http://emweb.securities.eastmoney.com/PC_HSF10/FinanceAnalysis/\
FinanceAnalysisAjax?code=%s&ctype=3'%code
    headers = {'Accept' : 'text/html,application/xhtml+xml,application/\
xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'emweb.securities.eastmoney.com',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/\
537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    html = getHTMLText(url,headers)
    html = html.replace(b'null',b'"null"')
    d = eval(html)
    d = d['Result']
    l = d['zyzb']
    for v in l:
        if v['date'] == '2016-12-31':
            price0 = v['jbmgsy']
            break
    price1 = l[0]['jbmgsy']
    return price0 < price1
    
    
def list2Frame(l):
    columns = ['flag','代码','名称','最新价','涨跌幅(%)',
               '主力净额(万元)','主力净占比(%)',
               '超大单净额(万元)','超大单净占比(%)',
               '大单净额(万元)','大单净占比(%)',
               '中单净额(万元)','中单净占比(%)',
               '小单净额(万元)','小单净占比(%)',
               'time','unknow','市盈']

    num_columns = ['最新价','涨跌幅(%)',
               '主力净额(万元)','主力净占比(%)',
               '超大单净额(万元)','超大单净占比(%)',
               '大单净额(万元)','大单净占比(%)',
               '中单净额(万元)','中单净占比(%)',
               '小单净额(万元)','小单净占比(%)',
               'unknow','市盈']
    result = []
    for row in l:
        r = row.split(',')
        code = r[1] + r[0]
        profit = getProfit(code)       
        r.append(profit)
        result.append(r)
    result = np.array(result)
    df = pd.DataFrame(data = result, columns=columns)
    df[num_columns] = df[num_columns].apply(pd.to_numeric, errors='ingnore')
    return df


def getStockInfo(code):
    headers = {'Accept' : '/*/',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'nufm.dfcfw.com',
               'Referer': 'http://quote.eastmoney.com/favor/default.html',
               'Cookie': cookie,
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/\
537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?\
ps=500&token=64a483cbad8b666efa51677820e6b21c&type=CT&\
cmd=%s&sty=CTBF&cb=getStockFullInfo&js=([(x)])&0.6878471248727867'%code
    html = getHTMLText(url,headers)
    l = eval(html.split(b'(')[1][:-1])
    result = []
    for row in l:
        r = row.split(',')
        result.append(r)

    columns = ['flag','代码','名称','最新价','涨跌幅','主力净流入(万)',
               '集合竞价','实时超大单流入','实时超大单流出',
               '实时超大单净额','实时超大单净占比',
               '实时大单流入','实时大单流出',
               '实时大单净额','实时大单净占比',
               '实时中单流入','实时中单流出',
               '实时中单净额','实时中单净占比',
               '实时小单流入','实时小单流出',
               '实时小单净额','实时小单净占比',]

    num_columns = ['最新价','主力净流入(万)',
               '集合竞价','实时超大单流入','实时超大单流出',
               '实时超大单净额',
               '实时大单流入','实时大单流出',
               '实时大单净额',
               '实时中单流入','实时中单流出',
               '实时中单净额',
               '实时小单流入','实时小单流出',
               '实时小单净额',]
    result = np.array(result)
    df = pd.DataFrame(data = result, columns=columns)
    df[num_columns] = df[num_columns].apply(pd.to_numeric, errors='ingnore')
    return df
    

def getStockInfo0(code):
    headers = {'Accept' : '/*/',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'nufm.dfcfw.com',
               'Referer': 'http://quote.eastmoney.com/favor/default.html',
               'Cookie': cookie,
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/\
537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?\
ps=500&token=580f8e855db9d9de7cb332b3990b61a3&type=CT&\
cmd=%s&sty=CTALL&cb=getStockFullInfo&js=([(x)])&0.5702436672405287'%code
    html = getHTMLText(url, headers)
    l = eval(html.split(b'(')[1][:-1])
    result = []
    for row in l:
        r = row.split(',')
        r.insert(0, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
        result.append(r)

    columns = ['time','flag','代码','名称','最新价','涨跌幅','涨跌额',
               '总手','现手','买入价','卖出价','涨速','换手','金额',
               '市盈率(动)','最高','最低','开盘','昨收',
               '振幅','量比','委比','委差','均价','内盘',
               '外盘','内外比','买一量','卖一量','市净率',
               '总股本','总市值','流通股本','流通市值',
               '3日涨幅','6日涨幅','3日换手','6日换手','end']

    num_columns = ['最新价','涨跌额',
               '总手','现手','买入价','卖出价','金额',
               '市盈率(动)','最高','最低','开盘','昨收',
               '量比','委差','均价','内盘',
               '外盘','内外比','买一量','卖一量','市净率',
               '总股本','总市值','流通股本','流通市值',]
    
    result = np.array(result)
    df = pd.DataFrame(data = result, columns=columns)
    df[num_columns] = df[num_columns].apply(pd.to_numeric, errors='ingnore')
    return df


def getStockDDE(code):
    headers = {'Accept' : '/*/',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'nufm.dfcfw.com',
               'Referer': 'http://quote.eastmoney.com/favor/default.html',
               'Cookie': cookie,
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/\
537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?\
ps=500&token=580f8e855db9d9de7cb332b3990b61a3&type=CT&\
cmd=%s&sty=CTDDE&cb=getStockFullInfo&js=([(x)])&0.481399740449725'%code
    
    html = getHTMLText(url, headers)
    l = eval(html.split(b'(')[1][:-1])
    result = []
    for row in l:
        r = row.split(',')
        result.append(r)

    columns = ['flag','代码','名称','最新价','涨跌幅',
               '当日DDX','当日DDY','当日DDZ','5日DDX','5日DDY',
               '10日DDX','10日DDY','DDX 飘红(连续)',
               'DDX飘红(5日)','DDX飘红(10日)',
               '特大买入','特大卖出','特大单净比',
               '大单买入','大单卖出','大单净比']
       
    result = np.array(result)
    df = pd.DataFrame(data = result, columns=columns)
    return df


def getMultiStockInfo(code):
    df0 = getStockInfo0(code)
    df1 = getStockInfo(code)
    df2 = getStockDDE(code)

    columns = ['flag','名称','最新价','涨跌幅']

    df3 = df0.drop(columns=columns)
    df4 = df2.drop(columns=columns)
    df = pd.merge(df3,df1,on='代码',how='outer')
    df = pd.merge(df,df4, on='代码',how='outer')
    
    return df, df0, df1, df2
    
    
if __name__ == '__main__':
    try:
        df = getPageInfo()
        df60 = df[df['市盈'] < 60]
        print('*'*20)
        print('市盈小于60的股票：')
        print(df60)
        myStock = getMyStock()
        for i in df60.head(50).index:
            code = df60.head(50)['代码'][i]
            flag = df60.head(50)['flag'][i]
            if (code+flag) not in myStock and isHighThanPre(code, flag):
                print(df60.head(50)['名称'][i], ' 不在自选中，加入自选')
                add2MyStock(code+'|0'+ flag +'|01')
        myStock = getMyStock()
        df , df0, df1, df2 = getMultiStockInfo(','.join(myStock))
        print()
        print()
        print('自选详细信息：')
        print(df)
        writer = pd.ExcelWriter('data.xlsx')
        df.to_excel(writer, 'Sheet1')
        df0.to_excel(writer, 'Ex2')
        df1.to_excel(writer, 'MO2')
        df2.to_excel(writer, 'DDE2')
        writer.save()
    
        while True:
            try:
                for i in range(300,0,-1):
                    sys.stdout.write('{:0>3}'.format(str(i)) + ' s\r')
                    sys.stdout.flush()
                    time.sleep(1)
                info = getPageInfo()
                df60 = info[info['市盈'] < 60]
                print('*'*20)
                print('市盈小于60的股票：')
                print(df60)
                myStock = getMyStock()
                for i in df60.head(50).index:
                    code = df60.head(50)['代码'][i]
                    flag = df60.head(50)['flag'][i]
                    if (code+flag) not in myStock and isHighThanPre(code, flag):
                        print(df60.head(50)['名称'][i], ' 不在自选中，加入自选')
                        add2MyStock(code+'|0'+ flag +'|01')
                myStock = getMyStock()
                ddf , ddf0, ddf1, ddf2 = getMultiStockInfo(','.join(myStock))
                print()
                print()
                print('自选详细信息：')
                print(ddf)
                writer = pd.ExcelWriter('data.xlsx')
                df = pd.concat([df, ddf])
                df0 = pd.concat([df0, ddf0])
                df1 = pd.concat([df1, ddf1])
                df2 = pd.concat([df2, ddf2])
                df.to_excel(writer, 'Sheet1')
                df0.to_excel(writer, 'Ex2')
                df1.to_excel(writer, 'MO2')
                df2.to_excel(writer, 'DDE2')
                writer.save()
            except Exception as e:
                print(str(e))
                pass
    except Exception as e:
        print(str(e))
    
