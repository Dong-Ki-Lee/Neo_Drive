import pymysql
import logstash
import logging
import time
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
# if use intranet only, use host name monitoring server
ip = s.getsockname()[0]
ip_tuple = (('CLIENT_IP', ip),)
print(ip)
s.close()

conn = pymysql.connect(host='localhost', user='monitoring', password='monitoringtest', charset='utf8')

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.LogstashHandler("164.125.14.150", 5958, version=1))

curs = conn.cursor()
while True:
    sql = 'show status;'
    curs.execute(sql)
    rows = curs.fetchall()
    test_logger.info(rows+ip_tuple)
    print(rows+ip_tuple)

    sql = 'show processlist;'
    curs.execute(sql)
    rows = curs.fetchall()
#    test_logger.info(rows)

    print(rows)

    time.sleep(5)

conn.close()


