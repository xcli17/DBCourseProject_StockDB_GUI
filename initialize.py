#!/usr/bin/env python
# coding: utf-8

from GUI.utility import *


if __name__ == '__main__':
    conn=MySQLdb.connect(host='localhost',port=3306,user='root',passwd='root',use_unicode=1, charset='utf8')
    cur=conn.cursor()
    # cur.execute("drop database if exists stocks")
    cur.execute("create database if not exists stocks")
    cur.execute("use stocks")
    cur.execute("set names utf8")
    get_basic_info(cur)
    cur.execute('show triggers')
    tris = cur.fetchall()
    for tri in tris:
        cur.execute('drop trigger {}'.format(tri[0]))
    cur.execute('''create table if not exists basic_info as 
                       select * from basic_info_stock 
                       union all 
                       select * from basic_info_index''')
    cur.execute('alter table basic_info_stock add primary key (code)')
    cur.execute('alter table basic_info_index add primary key (code)')
    cur.execute('alter table basic_info add primary key (code)')
    cur.execute('alter table basic_info_stock add foreign key (code) references basic_info(code)')
    cur.execute('alter table basic_info_index add foreign key (code) references basic_info(code)')

    cur.execute('''create trigger del_stockOrindex
                           before delete on basic_info for each row
                           begin
                                if (select count(code) from basic_info_stock where code = old.code) = 1 then
                                    delete from basic_info_stock where code = old.code;
                                elseif (select count(code) from basic_info_index where code = old.code) = 1 then
                                    delete from basic_info_index where code = old.code;
                                end if;
                           end
                    ''')
    cur.execute('''create trigger update_stockOrindex
                           after update on basic_info for each row
                           begin
                                if (select count(code) from basic_info_stock where code = new.code) = 1 then
                                    update basic_info_stock set code_name=new.code_name, outDate=new.outDate, status=new.status where code = old.code;
                                elseif (select count(code) from basic_info_index where code = old.code) = 1 then
                                    update basic_info_index set code_name=new.code_name, outDate=new.outDate, status=new.status where code = old.code;
                                end if;
                           end
                    ''')
    cur.execute('''create trigger insert_stockOrindex
                           after insert on basic_info for each row
                           begin
                                if new.type = 1 then
                                    insert into basic_info_stock values(new.code,new.code_name,new.ipoDate,new.outDate,new.type,new.status);
                                elseif new.type = 2 then
                                    insert into basic_info_index values(new.code,new.code_name,new.ipoDate,new.outDate,new.type,new.status);
                                end if;
                           end
                    ''')
    df_s = read_sql(cur, 'basic_info_stock')
    df_i = read_sql(cur, 'basic_info_index')
    no_data_list = []
    for i in tqdm(range(int(df_s.shape[0]))):
        for freq in FREQS_IN_DB:
            df_data = get_stock_data(df_s['code'][i], freq, df_s['ipoDate'][i], df_s['outDate'][i], False)
            if df_data.shape[0] > 0:
                to_sql(cur, df_data, '_'.join(df_s['code'][i].split('.')) + '_{}'.format(freq))
            else:
                no_data_list.append((df_s['code'][i], freq))
            time.sleep(0.001)
    for i in tqdm(range(int(df_i.shape[0]))):
        for freq in FREQS_IN_DB:
            df_data = get_stock_data(df_i['code'][i], freq, df_i['ipoDate'][i], df_i['outDate'][i], False)
            if df_data.shape[0] > 0:
                to_sql(cur, df_data, '_'.join(df_i['code'][i].split('.')) + '_{}'.format(freq))
            else:
                no_data_list.append((df_i['code'][i], freq))
            time.sleep(0.001)
    print("Can't get data for: ", no_data_list)
    cur.execute(''' create table if not exists stock_data_template_d(
                    date datetime,
                    code char(9),
                    open double,
                    high double,
                    low double,
                    close double,
                    preclose double,
                    volume double,
                    amount double,
                    adjustflag int,
                    turn double,
                    tradestatus int,
                    pctChg double,
                    isST int
                )''')
    cur.execute(''' create table if not exists stock_data_template_wm(
                       date datetime,
                       code char(9),
                       open double,
                       high double,
                       low double,
                       close double,
                       volume double,
                       amount double,
                       adjustflag int,
                       turn double,
                       pctChg double
                   )''')
    cur.execute('''create table if not exists data_update_record(
                       date datetime,
                       code char(9),
                       table_name char(12),
                       operation varchar(10),
                       foreign key (code) references basic_info(code)
                   )''')
    cur.execute("show tables")
    tables = [x[0] for x in cur.fetchall() if x[0][-3].isdigit()]
    for table in tqdm(tables):
        try:
            cur.execute('alter table {} add primary key (date)'.format(table))
        except MySQLdb._exceptions.OperationalError:
            pass
        cur.execute('select max(date) from {}'.format(table))
        last_date = cur.fetchone()[0]
        cur.execute("select code from basic_info where code like '%{}%'".format(table.split('_')[1]))
        code = cur.fetchone()[0]
        cur.execute('insert into data_update_record values (%s,%s,%s,%s)', [last_date, code, table, 'Init'])
    cur.execute('''create trigger del_record
                        before delete on basic_info for each row
                        begin
                            delete from data_update_record where code = old.code;
                        end
                ''')
    cur.execute('drop database if exists users')
    cur.execute('create database if not exists users')
    cur.execute('use users')
    cur.execute('show triggers')
    tris=cur.fetchall()
    for tri in tris:
        cur.execute('drop trigger {}'.format(tri[0]))
    cur.execute("drop table if exists watch")
    cur.execute("drop table if exists login_info")
    cur.execute("drop table if exists login_record")
    cur.execute("drop table if exists info_change_record")
    cur.execute("drop table if exists info")
    cur.execute('''create table if not exists info(
                    username varchar(50) not null,
                    password varchar(50) not null,
                    email varchar(50),
                    phone varchar(50),
                    display_name varchar(50),
                    register_time datetime,
                    state int unsigned,
                    primary key(username)
               )''')
    cur.execute('''create table if not exists watch(
                    username varchar(50) not null,
                    code varchar(9) not null,
                    code_name varchar(7) not null,
                    type int not null,
                    primary key (username,code),
                    foreign key (username) references info(username)
               )''')
    cur.execute('''create table if not exists login_record(
                    username varchar(50) not null,
                    login_time datetime,
                    state int unsigned,
                    foreign key (username) references info(username)
               )''')
    cur.execute('''create table if not exists info_change_record(
                    username varchar(50) not null,
                    password varchar(50) not null,
                    email varchar(50),
                    phone varchar(50),
                    display_name varchar(50),
                    change_time datetime,
                    state int unsigned,
                    foreign key (username) references info(username)
                )''')
    cur.execute('''create trigger del_user
                       before delete on info for each row
                       begin
                            delete from watch where username = old.username;
                            delete from login_record where username = old.username;       
                            delete from info_change_record where username = old.username;    
                       end''')
    cur.execute('''create trigger info_add_recording
                        after insert on info for each row
                        begin
                            insert into info_change_record values (new.username,new.password,new.email,
                                                                    new.phone,new.display_name,now(),
                                                                    new.state);
                        end
                ''')
    cur.execute('''create trigger info_update_recording
                        after update on info for each row
                        begin
                            insert into info_change_record values (new.username,new.password,new.email,
                                                                    new.phone,new.display_name,now(),
                                                                    new.state);
                        end
                ''')
    cur.execute("insert into info values (%s,%s,%s,%s,%s,%s,%s)",
                ('admin', 'admin', '', '', '管理员', getNowTime(), 1))

    cur.execute('use stocks')
    cur.execute('''create trigger del_stock_watch
                       before delete on basic_info for each row
                       begin
                            delete from users.watch where code = old.code;  
                       end''')
    cur.close()
    conn.commit()
    conn.close()
    bs.logout()