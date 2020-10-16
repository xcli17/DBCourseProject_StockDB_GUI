#!/usr/bin/env python
# coding: utf-8

from headfiles import *

lg = bs.login()
date_format = "%Y-%m-%d"
datetime_format = "%Y%m%d%H%M"
FREQS_IN_DB = ['d', 'w', 'm']


def index_to_col(df, name):
    df.reset_index(inplace = True)
    df.rename({'index': name}, axis = 1, inplace = True)


def to_sql(cur, df, name):
    col_names = list(df.columns)
    col_types = []
    col_form = []
    for col in col_names:
        df_dtype = df[col].dtype
        if df_dtype == 'O':
            col_form.append("%s")
            uniques = df[col].apply(len).unique()
            if (uniques.shape[0] > 1):
                col_types.append("varchar({})".format(uniques.max() + 1))
            else:
                col_types.append("char({})".format(uniques[0]))
        elif df_dtype == "<M8[ns]":
            col_form.append("%s")
            col_types.append("datetime")
        elif df_dtype == "float64":
            col_form.append("%s")
            col_types.append("double")
        elif df_dtype == "int64":
            col_form.append("%s")
            col_types.append("int")
        else:
            print(col, dt_dtype)
    cols = list(zip(col_names, col_types))
    cols = [' '.join(x) for x in cols]
    cur.execute("drop table if exists {}".format(name))
    cur.execute("create table {}({})".format(name, ','.join(cols)))
    tups = df.values
    tups = [tuple(x) for x in tups]
    template = "insert into {} values({})".format(name, ','.join(col_form))
    cur.executemany(template, tups)

def add_to_sql(cur,df,tablename):
    col_form=[]
    for i in range(cur.execute("show fields from {}".format(tablename))):
        col_form.append("%s")
    tups = df.values
    tups = [tuple(x) for x in tups]
    template = "insert into {} values({})".format(tablename, ','.join(col_form))
    cur.executemany(template, tups)

def read_sql(cur, name):
    cur.execute("describe {}".format(name))
    names = [x[0] for x in cur.fetchall()]
    cur.execute("select * from {}".format(name))
    df = cur.fetchall()
    df = [list(x) for x in df]
    df = pd.DataFrame(df, columns = names)
    return df


def get_prefix(code):
    if code[0].isdigit():
        if code[0] == '6':
            return "sh."
        else:
            return "sz."
    else:
        print("Wrong Code")


def getDate(x):
    if len(x) >= 1:
        return datetime.datetime.strptime(x, date_format)
    else:
        return datetime.datetime.strptime('2200-01-01', date_format)


def getDatetime(x):
    if len(x) >= 12:
        return datetime.datetime.strptime(x[:12], datetime_format)
    else:
        return datetime.datetime.strptime('2200-01-01', date_format)


def getInt(x):
    if len(x) >= 1:
        return int(x)
    else:
        return 0


def getFloat(x):
    if len(x) >= 1:
        return float(x)
    else:
        return 0


def get_basic_info(cur):
    rs = bs.query_stock_basic()
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns = rs.fields)
    result['ipoDate'] = result['ipoDate'].apply(getDate)
    result['outDate'] = result['outDate'].apply(getDate)
    result['type'] = result['type'].apply(getInt)
    result['status'] = result['status'].apply(getInt)
    basic_info_stock = result[result['type'] == 1].reset_index(drop = True)
    basic_info_index = result[result['type'] == 2].reset_index(drop = True)
    to_sql(cur, basic_info_stock, 'basic_info_stock')
    to_sql(cur, basic_info_index, 'basic_info_index')


def get_stock_data(code, freq, start, end, echo = False):
    '''
    freq=d,w,m,5,15,30,60
    '''
    if freq == 'd':
        rs = bs.query_history_k_data_plus(code,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date = datetime.datetime.strftime(start, "%Y-%m-%d"),
                                          end_date = datetime.datetime.strftime(end, "%Y-%m-%d"),
                                          frequency = freq, adjustflag = "2")
        if echo:
            print('query_history_k_data_plus respond error_code:' + rs.error_code)
            print('query_history_k_data_plus respond error_msg:' + rs.error_msg)
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns = rs.fields)
        result['date'] = result['date'].apply(getDate)
        for col in ["open", "high", "low", "close", "preclose", "volume", "amount", "turn", "pctChg"]:
            result[col] = result[col].apply(getFloat)
        for col in ["adjustflag", "tradestatus", "isST"]:
            result[col] = result[col].apply(getInt)
        return result
    elif freq in ['w', 'm']:
        rs = bs.query_history_k_data_plus(code,
                                          "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg",
                                          start_date = datetime.datetime.strftime(start, "%Y-%m-%d"),
                                          end_date = datetime.datetime.strftime(end, "%Y-%m-%d"),
                                          frequency = freq, adjustflag = "2")
        if echo:
            print('query_history_k_data_plus respond error_code:' + rs.error_code)
            print('query_history_k_data_plus respond error_msg:' + rs.error_msg)
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns = rs.fields)
        result['date'] = result['date'].apply(getDate)
        for col in ["open", "high", "low", "close", "volume", "amount", "turn", "pctChg"]:
            result[col] = result[col].apply(getFloat)
        for col in ["adjustflag"]:
            result[col] = result[col].apply(getInt)
        return result
    else:
        rs = bs.query_history_k_data_plus(code,
                                          "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                          start_date = datetime.datetime.strftime(start, "%Y-%m-%d"),
                                          end_date = datetime.datetime.strftime(end, "%Y-%m-%d"),
                                          frequency = freq, adjustflag = "2")
        if echo:
            print('query_history_k_data_plus respond error_code:' + rs.error_code)
            print('query_history_k_data_plus respond error_msg:' + rs.error_msg)
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns = rs.fields)
        result['date'] = result['date'].apply(getDate)
        result['time'] = result['time'].apply(getDatetime)
        for col in ["open", "high", "low", "close", "volume", "amount"]:
            result[col] = result[col].apply(getFloat)
        for col in ["adjustflag"]:
            result[col] = result[col].apply(getInt)
        return result

def getNowTime():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def getInit(cur):
    cur.execute('use stocks')
    rs = bs.query_stock_basic()
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns = rs.fields)
    if result.shape[0] == 0:
        return None, False
    cur.execute('select code from basic_info')
    indb_codes=[x[0] for x in cur.fetchall()]
    newcodes=list(set(result['code'].values)-set(indb_codes))
    if len(newcodes) == 0:
        return None, None, False
    result = result[result['code'].apply(lambda x: x in newcodes)]
    result['ipoDate'] = result['ipoDate'].apply(getDate)
    result['outDate'] = result['outDate'].apply(getDate)
    result['type'] = result['type'].apply(getInt)
    result['status'] = result['status'].apply(getInt)
    add_to_sql(cur, result, 'basic_info')
    now = datetime.datetime.today()
    codes=result['code'].values
    names=result['code_name'].values
    for i in range(result.shape[0]):
        code=codes[i]
        for freq in FREQS_IN_DB:
            # print(freq)
            df_data = get_stock_data(code = code, freq = freq, start = result['ipoDate'].iloc[i], end = now, echo = False)
            # print(df_data.shape)
            if df_data.shape[0] > 0:
                table_name = '_'.join(code.split('.')) + '_{}'.format(freq)
                # print(table_name)
                to_sql(cur, df_data, table_name)
                cur.execute('alter table {} add primary key (date)'.format(table_name))
                cur.execute('select max(date) from {}'.format(table_name))
                last_date = cur.fetchone()[0]
                cur.execute('insert into data_update_record values (%s,%s,%s,%s)', [last_date, code, table_name, 'Init'])
    return names,codes,True

def getUpdate(cur,code):
    cur.execute('use stocks')
    cur.execute("select * from stocks.basic_info where code = '{}'".format(code))
    stock_info = list(cur.fetchone())
    name=stock_info[1]
    cur.execute("select max(date) from stocks.data_update_record where code = '{}'".format(code))
    last_date = cur.fetchone()[0]
    now = datetime.datetime.today()
    if (now - datetime.timedelta(days = 1)) < last_date:
        return name, None, False
    rs = bs.query_stock_basic(code)
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns = rs.fields)
    result['ipoDate'] = result['ipoDate'].apply(getDate)
    result['outDate'] = result['outDate'].apply(getDate)
    if result['outDate'][0] < now:
        return name,None,False
    result['status'] = result['status'].apply(getInt)
    cur.execute("update basic_info set code_name='{}', outDate='{}', status='{}' where code = '{}'".format(
        result['code_name'][0],result['outDate'][0],result['status'][0],code))
    for freq in FREQS_IN_DB:
        df=get_stock_data(code = code, freq = freq, start = last_date, end = now)
        df=df[df['date']>last_date]
        add_to_sql(cur,df,'_'.join(code.split('.'))+'_'+freq)
        cur.execute("insert into data_update_record values (%s,%s,%s,%s)",(now,stock_info[0],'_'.join(code.split('.'))+'_'+freq,'Update'))
    return name, now, True

def getDelete(cur,code):
    cur.execute('use stocks')
    cur.execute("select code, code_name from stocks.basic_info where code like '{}'".format(code))
    stock_info = list(cur.fetchone())
    for freq in FREQS_IN_DB:
        cur.execute('drop table {}'.format('_'.join(code.split('.'))+'_'+freq))
    cur.execute("delete from basic_info where code = '{}'".format(stock_info[0]))
    return stock_info[1]
