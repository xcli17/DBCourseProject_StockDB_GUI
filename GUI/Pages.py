#!/usr/bin/env python
# coding: utf-8

from Frames import *

class LoginPage(object):
    def __init__(self, master = None, connect = None):
        self.root = master  # 定义内部变量root
        self.conn = connect
        self.root.geometry('%dx%d' % (500, 240))  # 设置窗口大小
        self.username = StringVar()
        self.password = StringVar()
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)  # 创建Frame
        self.page.pack()
        Label(self.page).grid(row = 0, rowspan=2, sticky="w")
        Label(self.page, text = '账户: ', height = 2, font=(None, 13)).grid(row = 2, rowspan=2, sticky="w", pady = 5)
        Entry(self.page, textvariable = self.username, ).grid(row = 2, rowspan=2, column = 1, sticky="e")
        Label(self.page, text = '密码: ', height = 2, font=(None, 13)).grid(row = 4, rowspan=2, sticky="w", pady = 5)
        Entry(self.page, textvariable = self.password, show = '*').grid(row = 4, rowspan=2, column = 1, sticky="e")
        Button(self.page, text = '登陆', command = self.loginCheck, width=10, font=(None, 13)).grid(row = 6, column=0, columnspan = 1, pady = 2)
        Button(self.page, text = '注册', command = self.tosigninPage, width = 10, font=(None, 13)).grid(row = 6, column = 1, columnspan = 1, pady = 2)
        Button(self.page, text = '找回密码', command = self.resetPassword, width = 10, font = (None, 13)).grid(row = 7, column = 0, columnspan = 1, pady = 2)
        Button(self.page, text = '退出', command = self.page.quit, width=10, font=(None, 13)).grid(row = 7, column=1, columnspan = 1, pady = 2)


    def loginCheck(self):
        username = self.username.get()
        password = self.password.get()
        cur = self.conn.cursor()
        cur.execute("use users")
        if cur.execute("select * from info where username = '{}' and password = '{}'".format(username, password)) == 1:
            user = cur.fetchone()
            cur.execute("insert into login_record values (%s,now(),%s)",(username,user[6]))
            if user[6] == 1:
                showinfo(title = 'welcome', message = '欢迎您：' + user[4])
                self.page.destroy()
                MainPage(self.root, self.conn, username)
            else:
                showinfo(title = 'welcome', message = '您的登录权限被管理员限制，请询问管理员以解禁')
        elif cur.execute("select * from info where username = '{}'".format(username)) == 1:
            showinfo(message = '密码错误：' + username)
        else:
            showinfo(message = '用户名错误，用户不存在：' + username)
        cur.close()

    def tosigninPage(self):
        SigninPage(self.root, self.conn)

    def resetPassword(self):
        CheckPage(self.root, self.conn)

class SigninPage(object):
    def __init__(self, master = None, connect = None):
        self.root = Toplevel(master)
        self.root.geometry('500x280')
        self.root.title('注册')
        self.conn = connect
        self.username = StringVar()
        self.password = StringVar()
        self.password_check = StringVar()
        self.email = StringVar()
        self.phone = StringVar()
        self.dispname = StringVar()
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack()
        Label(self.page, text = '请输入账户信息：').grid(row = 0, sticky = "w", pady = 5)
        Label(self.page, text = '账户: ').grid(row = 1, sticky = "w", pady = 5)
        Entry(self.page, textvariable = self.username).grid(row = 1, column = 1, sticky = "e")
        Label(self.page, text = '密码: ').grid(row = 2, sticky = "w", pady = 5)
        Entry(self.page, textvariable = self.password).grid(row = 2, column = 1, sticky = "e")
        Label(self.page, text = '确认密码: ').grid(row = 3, sticky = "w", pady = 5)
        Entry(self.page, textvariable = self.password_check).grid(row = 3, column = 1, sticky = "e")
        Label(self.page, text = '邮箱: ').grid(row = 4, sticky = "w", pady = 5)
        Entry(self.page, textvariable = self.email).grid(row = 4, column = 1, sticky = "e")
        Label(self.page, text = '电话: ').grid(row = 5, sticky = "w", pady = 5)
        Entry(self.page, textvariable = self.phone).grid(row = 5, column = 1, sticky = "e")
        Label(self.page, text = '显示名称: ').grid(row = 6, sticky = "w", pady = 5)
        Entry(self.page, textvariable = self.dispname).grid(row = 6, column = 1, sticky = "e")
        Button(self.page, text = '确认注册', command = self.signinCheck, width = 15).grid(row = 7, column = 0,
                                                                                      columnspan = 2, pady = 2)

    def signinCheck(self):
        username = self.username.get()
        password = self.password.get()
        password_check = self.password_check.get()
        email = self.email.get()
        phone = self.phone.get()
        dispname = self.dispname.get()
        cur = self.conn.cursor()
        cur.execute('use users')
        if len(username) > 50:
            showinfo(message = "用户名过长，请输入50个字符以内的用户名")
            cur.close()
            return
        if len(password) > 50:
            showinfo(message = "密码过长，请输入50个字符以内的密码")
            cur.close()
            return
        if cur.execute("select * from info where username = '{}'".format(username)) == 1:
            showinfo(message = "用户名已被使用，请重新输入用户名")
            cur.close()
            return
        elif password != password_check:
            showinfo(message = "两次输入的密码不同，请检查并重新输入")
            cur.close()
            return
        else:
            if len(dispname) < 1:
                dispname = username
            cur.execute('use users')
            cur.execute("insert into info values (%s,%s,%s,%s,%s,%s,%s)",
                        (username, password, email, phone, dispname,
                         time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 1))
            cur.close()
            self.conn.commit()
            self.page.destroy()
            self.root.destroy()
            showinfo(message = "注册成功，请在登录页面登录，{}".format(dispname))

class CheckPage(object):
    def __init__(self, master= None, connect =None):
        self.master=master
        self.root = Toplevel(master)
        self.root.geometry('300x200')
        self.root.title('验证密保信息')
        self.conn = connect
        self.username = StringVar()
        self.email = StringVar()
        self.phone = StringVar()
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)
        self.page.pack()
        Label(self.page, text = '请输入密保信息：').grid(row = 0, sticky = "w", pady = 10)
        Label(self.page, text = '账户: ').grid(row = 1, sticky = "w", pady = 5)
        Entry(self.page, textvariable = self.username).grid(row = 1, column = 1, sticky = "e")
        Label(self.page, text = '邮箱: ').grid(row = 2, sticky = "w", pady = 10)
        Entry(self.page, textvariable = self.email).grid(row = 2, column = 1, sticky = "e")
        Label(self.page, text = '电话: ').grid(row = 3, sticky = "w", pady = 10)
        Entry(self.page, textvariable = self.phone).grid(row = 3, column = 1, sticky = "e")
        Button(self.page, text = '确定', command=self.check,width=20).grid(row=4,columnspan=2)

    def check(self):
        username=self.username.get()
        email=self.email.get()
        phone=self.phone.get()
        cur = self.conn.cursor()
        cur.execute('use users')
        if len(username) > 50:
            showinfo(message = "用户名错误")
            cur.close()
            return
        elif cur.execute("select * from info where username = '{}'".format(username)) < 1:
            showinfo(message = "用户名不存在")
            cur.close()
            return
        else:
            userinfo=cur.fetchone()
            if email==userinfo[2] or phone == userinfo[3]:
                ResetPage(self.master,self.conn,username)
                self.page.destroy()
                self.root.destroy()
            else:
                showinfo(message = '密保信息错误，请检查后重新输入')

class ResetPage(object):
    def __init__(self, master = None, connect = None, username = None):
        self.root = Toplevel(master)
        self.root.geometry('300x200')
        self.root.title('设置新密码')
        self.conn = connect
        self.user = username
        self.password = StringVar()
        self.password_check = StringVar()
        self.createPage()

    def createPage(self):
        self.page=Frame(self.root)
        self.page.pack()
        Label(self.page, text = '请输入新密码：').grid(row = 0, sticky = "w", pady = 10)
        Label(self.page, text = '密码: ').grid(row = 1, sticky = "w", pady = 5)
        Entry(self.page, textvariable = self.password).grid(row = 1, column = 1, sticky = "e")
        Label(self.page, text = '确认密码: ').grid(row = 2, sticky = "w", pady = 10)
        Entry(self.page, textvariable = self.password_check).grid(row = 2, column = 1, sticky = "e")
        Button(self.page, text = '确定', command = self.reset, width = 20).grid(row = 3, columnspan = 2)

    def reset(self):
        password=self.password.get()
        password_check=self.password_check.get()
        cur=self.conn.cursor()
        cur.execute("use users")
        if len(password) > 50:
            showinfo(message = "密码过长，请输入50个字符以内的密码")
            cur.close()
            return
        elif password != password_check:
            showinfo(message = "两次输入的密码不同，请检查并重新输入")
            cur.close()
        else:
            cur.execute("update info set password = '{}' where username = '{}'".format(password,self.user))
            cur.close()
            self.conn.commit()
            self.page.destroy()
            self.root.destroy()
            showinfo(message = "密码重置成功，请在登录页面登录")

class MainPage(object):
    def __init__(self, master = None,connect=None, username = None):
        self.root = master
        self.conn=connect
        self.user=username
        self.adminFlag=(self.user=='admin')
        self.root.geometry('%dx%d' % (1024, 600))  # 设置窗口大小
        self.createPage()

    def createPage(self):
        self.watchPage = watchFrame(self.root, self.conn, self.user)
        self.addWatchPage = addWatchFrame(self.root, self.conn, self.user)
        self.plotPage = plotFrame(self.root, self.conn, self.user)
        self.changeinfoPage = changeInfoFrame(self.root, self.conn, self.user)
        self.adminUserPage = adminUserFrame(self.root, self.conn)
        self.adminDataPage = adminDataFrame(self.root, self.conn)
        self.adminRecordPage = adminRecordFrame(self.root,self.conn)
        self.watchPage.pack()
        menubar = Menu(self.root)
        menubar.add_command(label = '查看自选股', command = self.towatchPage)
        menubar.add_command(label = '添加自选股', command = self.toaddWatchPage)
        menubar.add_command(label = '股票走势绘图', command = self.toplotPage)
        menubar.add_command(label = '个人信息维护', command = self.tochangeinfoPage)
        if self.adminFlag:
            menubar.add_command(label = '管理员-用户管理操作', command = self.toadminUserPage)
            menubar.add_command(label = '管理员-数据库管理操作', command = self.toadminDataPage)
            menubar.add_command(label = '管理员-用户记录查看操作', command = self.toadminRecordPage)
        menubar.add_command(label = '退出登录', command = self.tologinPage)
        menubar.add_command(label = '退出程序', command = self.root.quit)
        self.root['menu'] = menubar

    def towatchPage(self):
        self.watchPage.pack()
        self.addWatchPage.pack_forget()
        self.plotPage.pack_forget()
        self.changeinfoPage.pack_forget()
        self.adminUserPage.pack_forget()
        self.adminDataPage.pack_forget()
        self.adminRecordPage.pack_forget()

    def toaddWatchPage(self):
        self.watchPage.pack_forget()
        self.addWatchPage.pack()
        self.plotPage.pack_forget()
        self.changeinfoPage.pack_forget()
        self.adminUserPage.pack_forget()
        self.adminDataPage.pack_forget()
        self.adminRecordPage.pack_forget()

    def toplotPage(self):
        self.watchPage.pack_forget()
        self.addWatchPage.pack_forget()
        self.plotPage.pack()
        self.changeinfoPage.pack_forget()
        self.adminUserPage.pack_forget()
        self.adminDataPage.pack_forget()
        self.adminRecordPage.pack_forget()

    def tochangeinfoPage(self):
        self.watchPage.pack_forget()
        self.addWatchPage.pack_forget()
        self.plotPage.pack_forget()
        self.changeinfoPage.pack()
        self.adminUserPage.pack_forget()
        self.adminDataPage.pack_forget()
        self.adminRecordPage.pack_forget()

    def toadminUserPage(self):
        self.watchPage.pack_forget()
        self.addWatchPage.pack_forget()
        self.plotPage.pack_forget()
        self.changeinfoPage.pack_forget()
        self.adminUserPage.pack()
        self.adminDataPage.pack_forget()
        self.adminRecordPage.pack_forget()

    def toadminDataPage(self):
        self.watchPage.pack_forget()
        self.addWatchPage.pack_forget()
        self.plotPage.pack_forget()
        self.changeinfoPage.pack_forget()
        self.adminUserPage.pack_forget()
        self.adminDataPage.pack()
        self.adminRecordPage.pack_forget()

    def toadminRecordPage(self):
        self.watchPage.pack_forget()
        self.addWatchPage.pack_forget()
        self.plotPage.pack_forget()
        self.changeinfoPage.pack_forget()
        self.adminUserPage.pack_forget()
        self.adminDataPage.pack_forget()
        self.adminRecordPage.pack()

    def tologinPage(self):
        self.watchPage.destroy()
        self.addWatchPage.destroy()
        self.plotPage.destroy()
        self.changeinfoPage.destroy()
        self.adminUserPage.destroy()
        self.adminDataPage.destroy()
        self.adminRecordPage.destroy()
        self.root['menu'] = []
        LoginPage(self.root,self.conn)