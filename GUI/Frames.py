#!/usr/bin/env python
# coding: utf-8

from utility import *

class watchFrame(Frame):
    def __init__(self, master = None, connect=None, username = None):
        Frame.__init__(self, master)
        self.root = master
        self.conn =connect
        self.user=username
        self.inputdate=StringVar()
        self.columns=['code','open','high','low','close','preclose','volume','amount','turn','pctChg']
        self.colstr=','.join(self.columns)
        self.colnames = ['代码', '开盘价', '最高价', '最低价', '收盘价', '前日收盘价', '交易量', '总量', '换手率', '价格变化']
        self.createPage()

    def createPage(self):
        Label(self).grid(row = 0, stick = W, pady = 10)
        Label(self, text = '请输入日期(要求格式为YYYYMMDD)').grid(row = 1, pady = 10)
        Entry(self, textvariable = self.inputdate).grid(row = 1, column = 1)
        Button(self, text = '确定', width = 15, command = self.searchForStocks).grid(row = 1, column = 2)
        Label(self, text = '自选股日线数据查询结果：').grid(row = 2, pady = 10)
        self.tree=Treeview(self)
        self.tree.grid(row=3, rowspan=10, column=0, columnspan=5)
        self.tree['columns']=self.columns
        for i,col in enumerate(self.columns):
            self.tree.column(col,width=80)
            self.tree.heading(col,text=self.colnames[i])

    def searchForStocks(self):
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        try:
            date=datetime.datetime.strptime(self.inputdate.get(),'%Y%m%d')
        except ValueError:
            showinfo(message = '日期格式错误，请输入正确格式的日期！')
            return
        cur=self.conn.cursor()
        cur.execute('use users')
        cur.execute("select * from watch where username = '{}'".format(self.user))
        userstocks=cur.fetchall()
        if len(userstocks) > 0:
            cur.execute('use stocks')
            for i in range(len(userstocks)):
                stock_code = '_'.join(userstocks[i][1].split('.'))
                stock_name=userstocks[i][2]
                try:
                    cur.execute("select {} from {} where date = '{}'".format(self.colstr,stock_code+'_d',date))
                    stock_record=cur.fetchone()
                    if stock_record:
                        stock_record=[stock_code]+list(stock_record)[1:]
                        self.tree.insert("", i, text = stock_name, values = stock_record)
                    else:
                        self.tree.insert("", i, text = stock_name, values = (stock_code,'-','-','-','-','-','-','-','-','-'))
                except MySQLdb._exceptions.ProgrammingError:
                    pass
            cur.close()
        else:
            cur.close()
            showinfo(message = '您还没有自选股，请前往添加自选股页面进行添加')
            return

class addWatchFrame(Frame):
    def __init__(self, master = None, connect=None, username = None):
        Frame.__init__(self, master)
        self.root = master
        self.conn = connect
        self.user = username
        self.user_input=StringVar()
        self.columns=['code','type','status']
        self.colnames=['代码','类型','交易状态']
        self.createPage()

    def createPage(self):
        Label(self).grid(row = 0, stick = W, pady = 10)
        Label(self, text = '股票(或指数)的名称或代码: ').grid(row = 1, pady = 10)
        Entry(self, textvariable = self.user_input).grid(row = 1, column = 1)
        Button(self,text ='确认添加',command=self.add_stock_to_watch,width=15).grid(row=2,column=0,columnspan=3,pady = 10)
        Button(self,text = '模糊查询',command=self.search_similar,width=15).grid(row=3,column=0,columnspan=3,pady = 10)
        self.tree = Treeview(self)
        self.tree.grid(row = 4, rowspan = 20, column = 0, columnspan = 3)
        self.tree['columns'] = self.columns
        for i, col in enumerate(self.columns):
            self.tree.column(col, width = 120)
            self.tree.heading(col, text = self.colnames[i])


    def add_stock_to_watch(self):
        user_input=self.user_input.get()
        cur=self.conn.cursor()
        cur.execute('use stocks')
        if cur.execute("select * from basic_info where code like '%{}%'".format(user_input)) == 1:
            stock = cur.fetchone()
        elif cur.execute("select * from basic_info where code_name like '%{}%'".format(user_input)) == 1:
            stock = cur.fetchone()
        else:
            cur.close()
            showinfo(message = '无法找到匹配的股票或匹配到多支股票，请输入准确的代码或名称')
            return
        cur.execute('use users')
        if cur.execute("select * from watch where username = '{}' and code = '{}'".format(self.user, stock[0])) == 0:
            cur.execute("insert into watch values (%s,%s,%s,%s)",(self.user, stock[0], stock[1], str(stock[4])))
            if stock[4] == 1:
                showinfo(message ='成功添加股票{}(代码：{})'.format(stock[1], stock[0]))
            else:
                showinfo(message ='成功添加指数{}(代码：{})'.format(stock[1], stock[0]))
        else:
            if stock[4] == 1:
                showinfo(message ='股票{}(代码：{})已在自选股列表中'.format(stock[1], stock[0].split('.')[1]))
            else:
                showinfo(message ='指数{}(代码：{})已在自选股列表中'.format(stock[1], stock[0].split('.')[1]))
        cur.close()
        self.conn.commit()

    def search_similar(self):
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        cur=self.conn.cursor()
        cur.execute("use stocks")
        user_input = self.user_input.get()
        if user_input[0].isdigit() or user_input[-1].isdigit():
            cur.execute('''
            select code_name,code,type,status from basic_info_stock where code like '%{}%'
            union
            select code_name,code,type,status from basic_info_index where code like '%{}%'
            '''.format(user_input,user_input))
        else:
            cur.execute('''
            select code_name,code,type,status from basic_info_stock where code_name like '%{}%'
            union
            select code_name,code,type,status from basic_info_index where code_name like '%{}%'
            '''.format(user_input, user_input))
        results = cur.fetchall()
        cur.close()
        if len(results)>0:
            for i in range(len(results)):
                line=list(results[i])
                if line[2] == 1:
                    line[2]='股票'
                else:
                    line[2]='指数'
                if line[3] == 1:
                    line[3]='可以交易'
                else:
                    line[3]='无法交易'
                self.tree.insert("", i, text=line[0], values=line[1:])
        else:
            showinfo(message = '没有与输入匹配的股票或指数')
            return

class plotFrame(Frame):
    def __init__(self, master = None, connect=None, username = None):
        Frame.__init__(self, master)
        self.root = master
        self.conn =connect
        self.user=username
        self.stock=StringVar()
        self.start_date=StringVar()
        self.end_date=StringVar()
        self.freq=IntVar()
        self.freqs=['Daily','Weekly','Monthly']
        self.all_index=['MA','EMA','MACD','RSI']
        self.boolvars=[]
        for i in self.all_index:
            self.boolvars.append(BooleanVar())
        self.choose_index=[]
        self.index_coef={}
        self.index_data={}
        self.short_var1 = StringVar()
        self.long_var1 = StringVar()
        self.short_var2 = StringVar()
        self.long_var2 = StringVar()
        self.short_var3 = StringVar()
        self.long_var3 = StringVar()
        self.single_var3 = StringVar()
        self.short_var4 = StringVar()
        self.long_var4 = StringVar()
        self.single_var4 = StringVar()
        self.names=['date', 'open', 'high', 'low', 'close', 'volume']
        self.createPage()

    def createPage(self):
        Label(self,text='股票名称或代码：').grid(row = 0, sticky = 'w', pady = 10)
        Entry(self,textvariable=self.stock).grid(row=0,column=1)
        Label(self, text = '起止日期(YYYYMMDD)：').grid(row = 1, sticky = 'w', columnspan=1, pady = 10)
        Entry(self, textvariable = self.start_date).grid(row = 1, column = 1, padx=10)
        Entry(self, textvariable = self.end_date).grid(row = 1, column = 2)
        Label(self, text = '图中K线的时间长度：').grid(row = 2, sticky = 'w',pady = 10)
        for i,f in enumerate(self.freqs):
            Radiobutton(self,text=f,variable=self.freq,value=i).grid(row=2,column=i+1)
        Label(self, text = '图中显示的技术指标类型：').grid(row = 3, sticky = 'w',pady = 10)
        for i,index in enumerate(self.all_index):
            Checkbutton(self,text=index,variable=self.boolvars[i],width=15).grid(row=3, column=i+1)
        Label(self, text = '注：(1)不输入参数则使用默认参数；(2)MA和EMA同时只会显示一个，二者都存在时优先MA').grid(row = 4, columnspan=4, sticky = 'w', pady = 10)
        row=5
        Label(self,text='MA参数：').grid(row=row, sticky = 'w', pady = 3)
        row=row+1
        Label(self,text='短均线长度MA1=').grid(row=row, column = 0, sticky = 'e', pady = 3)
        Entry(self, textvariable = self.short_var1).grid(row = row, column = 1)
        Label(self,text='长均线长度MA2=').grid(row=row,sticky = 'e', column = 2, pady = 3)
        Entry(self, textvariable = self.long_var1).grid(row = row, column = 3)
        row = row + 1
        Label(self, text = 'EMA参数：').grid(row = row, sticky = 'w', pady = 3)
        row = row + 1
        Label(self, text = '短均线长度EMA1=').grid(row = row, column = 0, sticky = 'e', pady = 3)
        Entry(self, textvariable = self.short_var2).grid(row = row, column = 1)
        Label(self, text = '长均线长度EMA2=').grid(row = row, column = 2, sticky = 'e', pady = 3)
        Entry(self, textvariable = self.long_var2).grid(row = row, column = 3)
        row = row + 1
        Label(self, text = 'MACD参数：').grid(row = row, sticky = 'w', pady = 3)
        row = row + 1
        Label(self, text = '短均线长度EMA1=').grid(row = row, column = 0,sticky = 'e', pady = 3)
        Entry(self, textvariable = self.short_var3).grid(row = row, column = 1)
        Label(self, text = '长均线长度EMA2=').grid(row = row, column = 2,sticky = 'e', pady = 3)
        Entry(self, textvariable = self.long_var3).grid(row = row, column = 3)
        row = row + 1
        Label(self, text = '离差均线长度DEA=').grid(row = row, sticky = 'e', pady = 3)
        Entry(self, textvariable = self.single_var3).grid(row = row, column = 1)
        row = row + 1
        Label(self, text = 'RSI参数：').grid(row = row, sticky = 'w', pady = 3)
        row = row + 1
        Label(self, text = '时间长度N=').grid(row = row, sticky = 'e', pady = 3)
        Entry(self, textvariable = self.single_var4).grid(row = row, column = 1)
        row = row + 1
        Label(self, text = '上背离界限Up=').grid(row = row, column = 0,sticky = 'e', pady = 3)
        Entry(self, textvariable = self.short_var4).grid(row = row, column = 1)
        Label(self, text = '下背离界限Down=').grid(row = row, column = 2,sticky = 'e', pady = 3)
        Entry(self, textvariable = self.long_var4).grid(row = row, column = 3)
        row = row + 1
        Button(self, text = '绘图', width = 30, command = self.getPlots).grid(row = row, columnspan=5, pady=10)

    def getPlots(self):
        self.choose_index=[]
        self.index_coef={}
        self.index_data={}
        cur=self.conn.cursor()
        cur.execute('use stocks')
        user_input=self.stock.get()
        freq = self.freqs[self.freq.get()]
        start = self.start_date.get()
        end = self.end_date.get()
        boolvals = [x.get() for x in self.boolvars]
        for i in range(len(boolvals)):
            if boolvals[i]:
                self.choose_index.append(self.all_index[i])
                self.index_coef[self.all_index[i]]={}
                self.index_data[self.all_index[i]]={}
        if user_input[0].isdigit() or user_input[-1].isdigit():
            cur.execute('''
            select code,code_name,ipoDate,outDate from basic_info_stock where code like '%{}%'
            union
            select code,code_name,ipoDate,outDate from basic_info_index where code like '%{}%'
            '''.format(user_input,user_input))
        else:
            cur.execute('''
            select code,code_name,ipoDate,outDate from basic_info_stock where code_name like '%{}%'
            union
            select code,code_name,ipoDate,outDate from basic_info_index where code_name like '%{}%'
            '''.format(user_input, user_input))
        results = cur.fetchall()
        if len(results) > 1:
            cur.close()
            showinfo(message = '无法唯一匹配股票或指数，请输入准确的代码或名称')
            return
        elif len(results) < 0:
            cur.close()
            showinfo(message = '没有与输入匹配的股票或指数')
            return
        else:
            results=results[0]
            self.code=results[0]
            code='_'.join(self.code.split('.'))
            self.code_name=results[1]
            ipodate=results[2]
            outdate=results[3]
            try:
                start=datetime.datetime.strptime(start,"%Y%m%d")
                end=datetime.datetime.strptime(end,"%Y%m%d")
            except ValueError:
                showinfo(message = '日期格式错误，请输入正确格式的日期！')
                cur.close()
                return
            if freq == 'Daily':
                start_=max(start-datetime.timedelta(days=80),ipodate)
                end_=min(end+datetime.timedelta(days=80),outdate)+datetime.timedelta(days=2)
            elif freq == 'Weekly':
                start_ = max(start - datetime.timedelta(days = 30 * 7), ipodate)
                end_ = min(end + datetime.timedelta(days = 30 * 7), outdate)+datetime.timedelta(days=8)
            elif freq == 'Monthly':
                start_ = max(start - datetime.timedelta(days = 30 * 30), ipodate)
                end_ = min(end + datetime.timedelta(days = 30 * 30), outdate)+datetime.timedelta(days=32)
            cur.execute("describe {}_{}".format(code,freq[0].lower()))
            cur.execute("select {} from {}_{} where date between '{}' and '{}'".format(','.join(self.names), code, freq[0].lower(), start_, end_))
            self.raw_data=cur.fetchall()
            cur.close()
            self.raw_data=[list(x) for x in self.raw_data]
            self.raw_data=pd.DataFrame(self.raw_data,columns=self.names)
            self.raw_data['date_n']=mdates.date2num(self.raw_data['date'])
            self.take_date_bool=((self.raw_data['date']>=start)&(self.raw_data['date']<=end))
            self.getPlot()

    def getMA(self):
        if 'MA' in self.choose_index:
            MA1=self.short_var1.get()
            MA2=self.long_var1.get()
            try:
                MA1=int(MA1)
                MA2=int(MA2)
            except ValueError:
                MA1 = 10
                MA2 = 20
                showinfo(message = "未输入参数或输入参数有误，已为MA使用默认参数: MA1=10, EMA2=20")
            Av1=self.raw_data['close'].rolling(window=MA1).mean()[self.take_date_bool]
            Av2=self.raw_data['close'].rolling(window=MA2).mean()[self.take_date_bool]
            self.index_coef['MA'].update({'MA1':MA1,'MA2':MA2})
            self.index_data['MA'].update({'MA1':Av1,'MA2':Av2})

    def getEMA(self):
        if 'EMA' in self.choose_index:
            EMA1 = self.short_var2.get()
            EMA2 = self.long_var2.get()
            try:
                EMA1 = int(EMA1)
                EMA2 = int(EMA2)
            except ValueError:
                EMA1=12
                EMA2=26
                showinfo(message = "未输入参数或输入参数有误，已为EMA使用默认参数: EMA1=12, EMA2=26")
            EAv1 = self.raw_data['close'].ewm(span=EMA1).mean()[self.take_date_bool]
            EAv2 = self.raw_data['close'].ewm(span=EMA2).mean()[self.take_date_bool]
            self.index_coef['EMA'].update({'EMA1': EMA1, 'EMA2': EMA2})
            self.index_data['EMA'].update({'EMA1': EAv1, 'EMA2': EAv2})

    def getMACD(self):
        if 'MACD' in self.choose_index:
            EMA1=self.short_var3.get()
            EMA2=self.long_var3.get()
            DEA=self.single_var3.get()
            try:
                EMA1 = int(EMA1)
                EMA2 = int(EMA2)
                DEA = int(DEA)
            except ValueError:
                EMA1=12
                EMA2=26
                DEA=9
                showinfo(message = "未输入参数或输入参数有误，已为MACD使用默认参数: EMA1=12, EMA2=26, DEA=9")
            EAv1 = self.raw_data['close'].ewm(span = EMA1).mean()
            EAv2 = self.raw_data['close'].ewm(span = EMA2).mean()
            EDif = EAv1-EAv2
            EDea = EDif.rolling(window = DEA).mean()
            EDif = EDif[self.take_date_bool]
            EDea = EDea[self.take_date_bool]
            self.index_coef['MACD'].update({'EMA1': EMA1, 'EMA2': EMA2,'DIF':1, 'DEA': DEA})
            self.index_data['MACD'].update({'DIF': EDif, 'DEA': EDea})

    def getRSI(self):
        if 'RSI' in self.choose_index:
            N=self.single_var4.get()
            up=self.short_var4.get()
            down=self.long_var4.get()
            try:
                N = int(N)
                up = int(up)
                down = int(down)
            except ValueError:
                N=14
                up=70
                down=30
                showinfo(message = "未输入参数或输入参数有误，已为RSI使用默认参数: N=14, Up=70, Down=30")
            RSI=self.raw_data['close'].diff(periods=1)
            RSI_val=((RSI.apply(lambda x: max(x, 0)).rolling(window = N).mean())/ RSI.abs().rolling(window = N).mean())*100
            RSI_val=RSI_val[self.take_date_bool]
            self.index_coef['RSI'].update({'N': N, 'Up': up, 'Down': down})
            self.index_data['RSI'].update({'RSI': RSI_val})

    def getPlot(self):
        self.getMA()
        self.getEMA()
        self.getMACD()
        self.getRSI()
        select_date=self.raw_data['date_n'][self.take_date_bool].values
        window=Toplevel(self)
        window.geometry('1000x618')
        window.title("{}(代码：{})".format(self.code_name,self.code))
        fig = Figure(figsize=(18, 11),facecolor='#07000d')
        fig.set_tight_layout(True)
        canvas = FigureCanvasTkAgg(fig, master = window)
        canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = 1)
        # toolbar = NavigationToolbar2Tk(canvas, window)
        # toolbar.update()
        # canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = 1)
        # def on_key_press(event):
        #     print("you pressed {}".format(event.key))
        #     key_press_handler(event, canvas, toolbar)
        # canvas.mpl_connect("key_press_event", on_key_press)
        # def _quit():
        #     window.destroy()

        fig.clear()

        # maLeg = plt.legend(loc = 9, ncol = 2, prop = {'size': 7},
        #                    fancybox = True, borderaxespad = 0.)
        # maLeg.get_frame().set_alpha(0.4)
        # textEd = pylab.gca().get_legend().get_texts()
        # pylab.setp(textEd[0:5], color = 'w')
        ax1 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, facecolor='#07000d', fig = fig)
        if 'RSI' in self.choose_index:
            ax0 = plt.subplot2grid((6,4), (0,0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d', fig = fig)
            up_RSI = self.index_coef['RSI']['Up']
            down_RSI = self.index_coef['RSI']['Down']
            rsiCol = '#c1f9f7'
            posCol = '#386d13'
            negCol = '#8f2020'
            ax0.plot(select_date, self.index_data['RSI']['RSI'], rsiCol, linewidth = 1.5)
            ax0.fill_between(select_date, self.index_data['RSI']['RSI'], up_RSI, where = (self.index_data['RSI']['RSI'] >= up_RSI),
                             facecolor = negCol, edgecolor = negCol, alpha = 0.5)
            ax0.fill_between(select_date, self.index_data['RSI']['RSI'], down_RSI, where = (self.index_data['RSI']['RSI'] <= down_RSI),
                             facecolor = posCol, edgecolor = posCol, alpha = 0.5)
            ax0.axhline(up_RSI, color = negCol)
            ax0.axhline(down_RSI, color = posCol)
            ax0.set_yticks([down_RSI, up_RSI])
            ax0.yaxis.label.set_color("w")
            ax0.spines['bottom'].set_color("#5998ff")
            ax0.spines['top'].set_color("#5998ff")
            ax0.spines['left'].set_color("#5998ff")
            ax0.spines['right'].set_color("#5998ff")
            ax0.tick_params(axis = 'y', colors = 'w')
            ax0.tick_params(axis = 'x', colors = 'w')
            ax0.set_ylabel('RSI')
            # ax0.legend()
        if 'MA' in self.choose_index:
            Label1 = str(self.index_coef['MA']['MA1']) + ' SMA'
            Label2 = str(self.index_coef['MA']['MA2']) + ' SMA'
            ax1.plot(select_date, self.index_data['MA']['MA1'].values, '#e1edf9', label = Label1, linewidth = 1.5)
            ax1.plot(select_date, self.index_data['MA']['MA2'].values, '#4ee6fd', label = Label2, linewidth = 1.5)
        elif 'EMA' in self.choose_index:
            Label1 = str(self.index_coef['EMA']['EMA1']) + ' SEMA'
            Label2 = str(self.index_coef['EMA']['EMA2']) + ' SEMA'
            ax1.plot(select_date, self.index_data['EMA']['EMA1'].values, '#e1edf9', label = Label1, linewidth = 1.5)
            ax1.plot(select_date, self.index_data['EMA']['EMA2'].values, '#4ee6fd', label = Label2, linewidth = 1.5)
        if 'MACD' in self.choose_index:
            ax2 = plt.subplot2grid((6, 4), (5, 0), sharex = ax1, rowspan = 1, colspan = 4, facecolor = '#07000d', fig = fig)
            Label1 = 'DIF'
            Label2 = str(self.index_coef['MACD']['DEA']) + ' DEA'
            ax2.plot(select_date, self.index_data['MACD']['DIF'].values, label = Label1, color = '#4ee6fd', lw = 1)
            ax2.plot(select_date, self.index_data['MACD']['DEA'].values, label = Label2, color = '#e1edf9', lw = 1)
            ax2.fill_between(select_date, self.index_data['MACD']['DIF'] - self.index_data['MACD']['DEA'], 0,
                             alpha = 0.5,
                             facecolor = '#00ffe8', edgecolor = '#00ffe8')
            plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune = 'upper'))
            ax2.spines['bottom'].set_color("#5998ff")
            ax2.spines['top'].set_color("#5998ff")
            ax2.spines['left'].set_color("#5998ff")
            ax2.spines['right'].set_color("#5998ff")
            ax2.tick_params(axis = 'x', colors = 'w')
            ax2.tick_params(axis = 'y', colors = 'w')
            ax2.set_ylabel('MACD', color = 'w')
            ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins = 5, prune = 'upper'))
            # ax2.legend()
            # for label in ax2.xaxis.get_ticklabels():
            #     label.set_rotation(45)
        candlestick_ohlc(ax1, self.raw_data[['date_n', 'open', 'high', 'low', 'close']][self.take_date_bool].values,
                         width = .6, colorup = '#ff1717', colordown = '#53c156')
        ax1v = ax1.twinx()
        ax1v.fill_between(select_date, 0, self.raw_data['volume'][self.take_date_bool].values, facecolor = '#00ffe8',
                          alpha = .4)
        ax1.grid(True, color = 'w')
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.yaxis.label.set_color("w")
        ax1.spines['bottom'].set_color("#5998ff")
        ax1.spines['top'].set_color("#5998ff")
        ax1.spines['left'].set_color("#5998ff")
        ax1.spines['right'].set_color("#5998ff")
        ax1.tick_params(axis = 'y', colors = 'w')
        plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune = 'upper'))
        ax1.tick_params(axis = 'x', colors = 'w')
        ax1.set_ylabel('Stock price and Volume')
        ax1v.axes.yaxis.set_ticklabels([])
        ax1v.grid(False)
        ax1v.set_ylim(0, 3 * self.raw_data['volume'][self.take_date_bool].max())
        ax1v.spines['bottom'].set_color("#5998ff")
        ax1v.spines['top'].set_color("#5998ff")
        ax1v.spines['left'].set_color("#5998ff")
        ax1v.spines['right'].set_color("#5998ff")
        ax1v.tick_params(axis = 'x', colors = 'w')
        ax1v.tick_params(axis = 'y', colors = 'w')
        # fig.tight_layout(pad=0, h_pad = 1, w_pad=0)
        fig.legend(loc='best')
        canvas.draw()

class changeInfoFrame(Frame):
    def __init__(self, master = None, connect = None, username = None):
        Frame.__init__(self, master)
        self.root = master
        self.conn = connect
        self.user = username
        self.password = StringVar()
        self.password_check = StringVar()
        self.email = StringVar()
        self.phone = StringVar()
        self.dispname = StringVar()
        self.createPage()

    def createPage(self):
        Label(self).grid(row = 0, sticky = 'w', pady = 10)
        Label(self, text = '请输入需要修改的信息').grid(row = 1, sticky="w", pady = 5)
        Label(self, text = '密码: ').grid(row = 2, sticky="w", pady = 5)
        Entry(self, textvariable = self.password).grid(row = 2, column = 1, sticky="e")
        Label(self, text = '确认密码: ').grid(row = 3, sticky = "w", pady = 5)
        Entry(self, textvariable = self.password_check).grid(row = 3, column = 1, sticky = "e")
        Label(self, text = '邮箱: ').grid(row = 4, sticky = "w", pady = 5)
        Entry(self, textvariable = self.email).grid(row = 4, column = 1, sticky = "e")
        Label(self, text = '电话: ').grid(row = 5, sticky = "w", pady = 5)
        Entry(self, textvariable = self.phone).grid(row = 5, column = 1, sticky = "e")
        Label(self, text = '显示名称: ').grid(row = 6, sticky = "w", pady = 5)
        Entry(self, textvariable = self.dispname).grid(row = 6, column = 1, sticky = "e")
        Button(self, text = '确认修改', command = self.changeCheck, width = 15).grid(row = 7, column = 0, columnspan = 2, pady = 10)

    def changeCheck(self):
        cur=self.conn.cursor()
        cur.execute('use users')
        password = self.password.get()
        password_check = self.password_check.get()
        email = self.email.get()
        phone = self.phone.get()
        display_name = self.dispname.get()
        message="成功修改属性："
        if len(password) > 0:
            if len(password) > 50:
                showinfo(message = "密码过长，请输入50个字符以内的密码")
            elif password != password_check:
                showinfo(message = "两次输入的密码不同，请检查并重新输入")
            else:
                cur.execute("update info set password = '{}' where username = '{}'".format(password,self.user))
                message=message+'密码,'
        if len(email) > 0:
            if len(email) > 50:
                showinfo(message = "邮箱过长，请输入50个字符以内的邮箱")
            else:
                cur.execute("update info set email = '{}' where username = '{}'".format(email, self.user))
                message = message + '邮箱,'
        if len(phone) > 0:
            if len(phone) > 50:
                showinfo(message = "电话过长，请输入50个字符以内的电话")
            else:
                cur.execute("update info set phone = '{}' where username = '{}'".format(phone, self.user))
                message = message + '电话,'
        if len(display_name) > 0:
            if len(display_name) > 50:
                showinfo(message = "显示名称过长，请输入50个字符以内的显示名称")
            else:
                cur.execute("update info set display_name = '{}' where username = '{}'".format(display_name, self.user))
                message = message + '显示名称,'
        cur.close()
        self.conn.commit()
        showinfo(message = message)

class adminUserFrame(Frame):
    def __init__(self, master = None, connect = None):
        Frame.__init__(self, master)
        self.root = master
        self.conn = connect
        self.username=StringVar()
        self.chgusername = StringVar()
        self.password = StringVar()
        self.email = StringVar()
        self.phone = StringVar()
        self.dispname = StringVar()
        self.state = StringVar()
        self.columns = ['password','email','phone','dispname','state']
        self.colnames = ['密码', '邮箱', '电话', '显示名称', '状态']
        self.createPage()

    def createPage(self):
        Label(self).grid(row = 0, sticky = 'w', pady = 10)
        Label(self, text = '用户信息查看与修改页面').grid(row = 1, columnspan=2, sticky = "w", pady = 5)
        Label(self, text = '查看的账户的用户名(留空则查看所有): ').grid(row = 2, column = 0, columnspan=2, sticky = "w", pady = 5)
        Entry(self, textvariable = self.username).grid(row = 2, column = 2, sticky = "e")
        Button(self, text ='确定', command=self.search_similar).grid(row=2,column =3)
        self.tree = Treeview(self)
        self.tree.grid(row = 3, rowspan = 5, column = 0, columnspan = 8)
        self.tree['columns'] = self.columns
        for i, col in enumerate(self.columns):
            self.tree.column(col, width = 100)
            self.tree.heading(col, text = self.colnames[i])
        Label(self, text = '修改的账户的用户名: ').grid(row = 8, column = 0, columnspan = 1, sticky = "w", pady = 5)
        Entry(self, textvariable = self.chgusername).grid(row = 8, column = 1, sticky = "e")
        Label(self, text = '密码: ').grid(row = 9, sticky = "w", pady = 5)
        Entry(self, textvariable = self.password).grid(row = 9, column = 1, sticky = "e")
        Label(self, text = '邮箱: ').grid(row = 10, sticky = "w", pady = 5)
        Entry(self, textvariable = self.email).grid(row = 10, column = 1, sticky = "e")
        Label(self, text = '电话: ').grid(row = 11, sticky = "w", pady = 5)
        Entry(self, textvariable = self.phone).grid(row = 11, column = 1, sticky = "e")
        Label(self, text = '显示名称: ').grid(row = 12, sticky = "w", pady = 5)
        Entry(self, textvariable = self.dispname).grid(row = 12, column = 1, sticky = "e")
        Label(self, text = '状态: ').grid(row = 13, sticky = "w", pady = 5)
        Entry(self, textvariable = self.state).grid(row = 13, column = 1, sticky = "e")
        Button(self, text = '确认修改', command = self.changeCheck, width = 15).grid(row = 14, column = 0, columnspan = 2, pady = 5)
        Button(self,text = '删除用户', command = self.deluser, width=15).grid(row = 14, column = 2, columnspan = 2, pady = 5)

    def search_similar(self):
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        cur = self.conn.cursor()
        cur.execute("use users")
        username = self.username.get()
        cur.execute("select * from info where username like '%{}%'".format(username))
        results = cur.fetchall()
        cur.close()
        if len(results) > 0:
            for i in range(len(results)):
                line = list(results[i])
                line = line[:5]+[line[6]]
                self.tree.insert("", i, text = line[0], values = line[1:])
        else:
            showinfo(message = '没有与输入匹配的用户')
            return

    def changeCheck(self):
        cur = self.conn.cursor()
        cur.execute('use users')
        chgusername = self.chgusername.get()
        password = self.password.get()
        email = self.email.get()
        phone = self.phone.get()
        display_name = self.dispname.get()
        state = self.state.get()
        message = "成功修改属性："
        if cur.execute("select * from info where username = '{}'".format(chgusername)) == 0:
            showinfo(message = "所选择的用户不存在")
            cur.close()
            return
        if len(password) > 0:
            if len(password) > 50:
                showinfo(message = "密码过长，请输入50个字符以内的密码")
            else:
                cur.execute("update info set password = '{}' where username = '{}'".format(password, chgusername))
                message = message + '密码,'
        if len(email) > 0:
            if len(email) > 50:
                showinfo(message = "邮箱过长，请输入50个字符以内的邮箱")
            else:
                cur.execute("update info set email = '{}' where username = '{}'".format(email, chgusername))
                message = message + '邮箱,'
        if len(phone) > 0:
            if len(phone) > 50:
                showinfo(message = "电话过长，请输入50个字符以内的电话")
            else:
                cur.execute("update info set phone = '{}' where username = '{}'".format(phone, chgusername))
                message = message + '电话,'
        if len(display_name) > 0:
            if len(display_name) > 50:
                showinfo(message = "显示名称过长，请输入50个字符以内的显示名称")
            else:
                cur.execute("update info set display_name = '{}' where username = '{}'".format(display_name, chgusername))
                message = message + '显示名称,'
        if len(state) > 0:
            try:
                state=int(state)
                if state != 0:
                    state = 1
                cur.execute("update info set state = '{}' where username = '{}'".format(state, chgusername))
                message = message + '状态,'
            except ValueError:
                showinfo(message = "状态必须为整数")
        cur.close()
        self.conn.commit()
        showinfo(message = message)

    def deluser(self):
        cur=self.conn.cursor()
        cur.execute('use users')
        chgusername = self.chgusername.get()
        if cur.execute("select * from info where username = '{}'".format(chgusername)) == 0:
            showinfo(message = "所选择的用户不存在")
            cur.close()
            return
        cur.execute("delete from info where username='{}'".format(chgusername))
        cur.close()
        self.conn.commit()
        showinfo(message = "成功删除用户：{}".format(chgusername))

class adminDataFrame(Frame):
    def __init__(self, master = None, connect = None):
        Frame.__init__(self, master)
        self.root = master
        self.conn = connect
        self.stock = StringVar()
        self.chgstock=StringVar()
        self.columns = ['table_name','date','operation']
        self.colnames = ['表名', '最后更新时间', '操作']
        self.operation = IntVar()
        self.operations = ['Init','Update', 'Delete']
        self.opernames = ['添加','更新', '删除']
        self.suffix = ['_d','_w','_m']
        self.createPage()

    def createPage(self):
        Label(self).grid(row = 0, sticky = 'w', pady = 10)
        Label(self, text = '股票数据库信息查看与修改页面').grid(row = 1, columnspan=2, sticky = "w", pady = 5)
        Label(self, text = '查看股票/指数的更新记录(一次仅可查询一支): ').grid(row = 2, column = 0, columnspan = 2, sticky = "w", pady = 5)
        Entry(self, textvariable = self.stock).grid(row = 2, column = 2, sticky = "e")
        Button(self, text = '确定', width=15, command = self.search_similar).grid(row = 2, column = 3,padx=10)
        self.tree = Treeview(self)
        self.tree.grid(row = 3, rowspan = 5, column = 0, columnspan = 8)
        self.tree['columns'] = self.columns
        for i, col in enumerate(self.columns):
            self.tree.column(col, width = 150)
            self.tree.heading(col, text = self.colnames[i])
        Label(self, text = '操作的股票/指数代码: ').grid(row = 8, column = 0, columnspan = 1, sticky = "w", pady = 5)
        Entry(self, textvariable = self.chgstock).grid(row = 8, column = 1, sticky = "e")
        Label(self, text = '操作: ').grid(row = 9, sticky = "w", pady = 5)
        for i, op in enumerate(self.opernames):
            Radiobutton(self, text = op, variable = self.operation, value = i).grid(row = 9, column = i + 1)
        Label(self, text = "说明: (1)添加为添加所有不在当前数据库中的股票;").grid(row = 10, columnspan = 6, sticky = "w", pady = 5)
        Label(self, text = "      (2)更新为将指定股票/指数更新到当天；").grid(row = 11, columnspan = 6, sticky = "w", pady = 5)
        Label(self, text = "      (3)删除为删去指定股票/指数的所有数据").grid(row = 12, columnspan = 6, sticky = "w", pady = 5)
        Button(self, text = '确认操作', command = self.operCheck, width = 15).grid(row = 13, column = 0, columnspan = 6,
                                                                                 pady = 5)

    def search_similar(self):
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        cur = self.conn.cursor()
        cur.execute("use stocks")
        stock=self.stock.get()
        if stock[0].isdigit() or stock[-1].isdigit():
            cur.execute("select code from basic_info where code like '%{}%'".format(stock))
        else:
            cur.execute("select code from basic_info where code_name like '%{}%'".format(stock))
        results = cur.fetchall()
        if len(results) == 1:
            cur.execute("select code, table_name, date, operation from data_update_record where code = '{}'".format(results[0][0]))
            records = list(cur.fetchall())
            cur.close()
            # print(records)
            sorted(records,key=lambda x:x[2], reverse = True)
            for i in range(len(records)):
                self.tree.insert("", i, text = records[i][0], values = records[i][1:])
        else:
            showinfo(message = '没有匹配或匹配到多个股票或指数，请输入准确的代码或名称')
            cur.close()
            return

    def operCheck(self):
        opration=self.operations[self.operation.get()]
        chgstock=self.chgstock.get()
        code=chgstock
        if opration == 'Init':
            cur=self.conn.cursor()
            [names,codes,flag]=getInit(cur)
            if flag:
                message = "成功添加股票/指数{}(代码：{})\n"
                messages = ""
                for i in range(len(names)):
                    messages = messages + message.format(names[i],codes[i])
                showinfo(message = messages)
            else:
                showinfo(message = '没有找到不在数据库中的A股股票/指数')
                return
        elif not re.match(pattern='s[hz].\d\d\d\d\d\d',string=code):
            showinfo(message = '不合法的股票/指数代码')
            return
        else:
            cur = self.conn.cursor()
            if opration == 'Update':
                if cur.execute("select table_name from information_schema.tables where table_schema= 'stocks' and table_name like '%{}%'".format('_'.join(code.split('.')))) == 0:
                    showinfo(message = '数据库中无对应代码的股票/指数，请先添加')
                else:
                    [name, newdate, flag] = getUpdate(cur, code)
                    if flag:
                        showinfo(message = '成功更新股票/指数{}(代码：{})的数据至{}'.format(name, code, datetime.datetime.strftime(newdate,'%Y%m%d %H:%M:%S')))
                    else:
                        showinfo(message = '股票/指数{}(代码：{})的数据已经为最新，不需要更新'.format(name, code))
            elif opration == 'Delete':
                if cur.execute("select table_name from information_schema.tables where table_schema= 'stocks' and table_name like '%{}%'".format('_'.join(code.split('.')))) == 0:
                    showinfo(message = '数据库中无对应代码的股票/指数，请先添加')
                else:
                    name = getDelete(cur, code)
                    showinfo(message = '成功删除股票/指数{}(代码：{})'.format(name, code))
            cur.close()
            self.conn.commit()

class adminRecordFrame(Frame):
    def __init__(self, master = None, connect = None):
        Frame.__init__(self, master)
        self.root = master
        self.conn = connect
        self.username1=StringVar()
        self.username2=StringVar()
        self.password = StringVar()
        self.email = StringVar()
        self.phone = StringVar()
        self.dispname = StringVar()
        self.state = StringVar()
        self.columns = ['username','login_time','state']
        self.colnames = ['用户名','登录时间','登录状态']
        self.columns2 = ['username', 'password', 'email', 'phone', 'display_name', 'state', 'change_time']
        self.colnames2 = ['用户名', '密码', '邮箱', '电话', '显示名称', '状态', '修改时间']
        self.createPage()

    def createPage(self):
        Label(self, text = '用户登录与修改记录查看页面').grid(row = 0, columnspan=2, sticky = "w", pady = 5)
        Label(self, text = '查看的登录记录的用户名(留空则查看所有): ').grid(row = 1, column = 0, columnspan=2, sticky = "w", pady = 5)
        Entry(self, textvariable = self.username1).grid(row = 1, column = 2, sticky = "e")
        Button(self, text ='确定', command=self.getLoginRecrod).grid(row=1,column =3)
        self.tree = Treeview(self)
        self.tree.grid(row = 2, rowspan = 5, column = 0, columnspan = 8)
        self.tree['columns'] = self.columns
        for i, col in enumerate(self.columns):
            self.tree.column(col, width = 150)
            self.tree.heading(col, text = self.colnames[i])
        Label(self, text = '查看的修改记录的用户名(留空则查看所有): ').grid(row = 7, column = 0, columnspan = 2, sticky = "w", pady = 5)
        Entry(self, textvariable = self.username2).grid(row = 7, column = 2, sticky = "e")
        Button(self, text = '确定', command = self.getInfochgRecrod).grid(row = 7, column = 3)
        self.tree2 = Treeview(self)
        self.tree2.grid(row = 8, rowspan = 5, column = 0, columnspan = 8)
        self.tree2['columns'] = self.columns2
        for i, col in enumerate(self.columns2):
            self.tree2.column(col, width = 100)
            self.tree2.heading(col, text = self.colnames2[i])

    def getLoginRecrod(self):
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        cur = self.conn.cursor()
        cur.execute("use users")
        username = self.username1.get()
        cur.execute("select {} from login_record where username like '%{}%'".format(','.join(self.columns),username))
        results = cur.fetchall()
        cur.close()
        if len(results) > 0:
            for i in range(len(results)):
                line = list(results[i])
                self.tree.insert("", i, text = i, values = line)
        else:
            showinfo(message = '没有与输入匹配的用户')
            return

    def getInfochgRecrod(self):
        x = self.tree2.get_children()
        for item in x:
            self.tree2.delete(item)
        cur = self.conn.cursor()
        cur.execute("use users")
        username = self.username1.get()
        cur.execute("select {} from info_change_record where username like '%{}%'".format(','.join(self.columns2),username))
        results = cur.fetchall()
        cur.close()
        if len(results) > 0:
            for i in range(len(results)):
                line = list(results[i])
                self.tree2.insert("", i, text = i, values = line)
        else:
            showinfo(message = '没有与输入匹配的用户')
            return