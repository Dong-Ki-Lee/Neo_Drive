import socket
import pymysql

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
# if use intranet only, use host name monitoring server
ip = s.getsockname()[0]
ip_tuple = (('Local_IP', ip),)
print(ip)
s.close()

conn = pymysql.connect(host='localhost', user='monitoring', password='monitoringtest', charset='utf8')

curs = conn.cursor()
sql = 'show status;'
curs.execute(sql)
rows = curs.fetchall()
rows += ip_tuple
print(rows)

conn.close()


