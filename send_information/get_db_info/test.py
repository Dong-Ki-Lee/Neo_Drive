import pymysql
import time

conn = pymysql.connect(host='localhost', user='monitoring', password='monitoringtest', charset='utf8')

curs = conn.cursor()
while True:

    sql = 'show status;'
    curs.execute(sql)

    rows = curs.fetchall()
    print(rows)

    sql = 'show processlist;'
    curs.execute(sql)
    rows = curs.fetchall()
    print(rows)


conn.close()

