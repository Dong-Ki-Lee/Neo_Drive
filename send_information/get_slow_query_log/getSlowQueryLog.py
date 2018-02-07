import pymysql
import logstash
import logging
import time
import socket
import datetime

# Database ID and Password
DATABASE_ID = 'monitoring'
DATABASE_PW = 'monitoringtest'

MONITORING_SERVER_IP = '164.125.14.150'
MONITORING_SERVER_QUERY_INFO_LOGSTASH_PORT = 5956


def get_result_sql_execute(sql):
    try:
        conn = pymysql.connect(host='localhost', user=DATABASE_ID, password=DATABASE_PW, charset='utf8')
        cursor = conn.cursor()
        cursor.execute(sql)
        db_status_rows = cursor.fetchall()
        conn.close()
    except:
        db_status_rows = 'mysql connection error'
        print("error")
    finally:
        return db_status_rows


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    # if use intranet only, use host name monitoring server
    ip = s.getsockname()[0]
    s.close()
    return ip


query_logger = logging.getLogger('query_logstash')
query_logger.setLevel(logging.INFO)
query_logger.addHandler(logstash.LogstashHandler(
    MONITORING_SERVER_IP,
    MONITORING_SERVER_QUERY_INFO_LOGSTASH_PORT,
    version=1)
)

ip = get_ip_address()

while True:

    sql = 'select * from mysql.general_log'
    rows = get_result_sql_execute(sql)

    for row in rows:
        if row[4] == 'Query':
            if 'AUTOCOMMIT' in str(row[5]) or 'autocommit' in str(row[5]) or 'KILL' in str(row[5]):
                continue
            if 'SHOW' in str(row[5]) or 'show' in str(row[5]):
                continue
            if 'general_log' in str(row[5]):
                continue

            db_status_information = ()

            temp_tuple = (('OCCUR_TIME', (row[0] + datetime.timedelta(hours=-9)).strftime('%Y-%m-%dT%H:%M:%SZ')),)
            db_status_information += temp_tuple

            temp_tuple = (('USER', row[1]),)
            db_status_information += temp_tuple

            temp_tuple = (('QUERY', row[5]),)
            db_status_information += temp_tuple

            temp_tuple = (('CLIENT_IP', ip),)
            db_status_information += temp_tuple

            query_logger.info(db_status_information)
            print(db_status_information)
    time.sleep(600)

conn.close()
