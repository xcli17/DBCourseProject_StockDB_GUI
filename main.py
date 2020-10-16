# coding: utf-8

from GUI.Pages import *

def main():
    conn=MySQLdb.connect(host='localhost',port=3306,user='root',passwd='root',use_unicode=1, charset='utf8')
    root = Tk()
    root.title('看股小程序')
    LoginPage(root,conn)
    root.mainloop()
    conn.commit()
    conn.close()
    bs.logout()

if __name__ == '__main__':
    main()