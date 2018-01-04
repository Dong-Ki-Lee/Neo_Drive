import pymysql
import time
import logstash
import logging
import time

conn = pymysql.connect(host='localhost', user='monitoring', password='monitoringtest', charset='utf8')

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.LogstashHandler("164.125.14.151", 5958, version=1))

curs = conn.cursor()
while True:

    sql = 'show status;'
    curs.execute(sql)

    rows = curs.fetchall()
    print(rows)
    test_logger.info(rows)

    print("insert status data")
    sql = 'show processlist;'
    curs.execute(sql)
    rows = curs.fetchall()
    test_logger.info(rows)

    print("insert status data")
    print(rows)

    time.sleep(5)

conn.close()


