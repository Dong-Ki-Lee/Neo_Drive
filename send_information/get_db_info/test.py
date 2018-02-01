from pymongo import MongoClient
import pymysql
import logstash
import logging
import time
import socket

MONITORING_SERVER_IP = '164.125.14.150'
MONITORING_SERVER_MONGODB_PORT = 26543
MONITORING_SERVER_DB_INFO_LOGSTASH_PORT = 5958

DATABASE_ID = 'monitoring'
DATABASE_PW = 'monitoringtest'
# normal value
NORMAL = '0'

pre_questions = 0
pre_bytes_sent = 0
pre_bytes_received = 0
pre_created_tmp_disk_tables = 0
pre_connections = 0
pre_handler_read_rnd_next = 0
pre_com_select = 0


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    # if use intranet only, use host name monitoring server
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_ip_address_tuple():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    # if use intranet only, use host name monitoring server
    ip = s.getsockname()[0]
    ip_tuple = (('CLIENT_IP', ip),)
    s.close()
    return ip_tuple


def get_result_sql_execute(sql):
    sql_result = ''
    try:
        conn = pymysql.connect(host='localhost', user=DATABASE_ID, password=DATABASE_PW, charset='utf8')
        cursor = conn.cursor()
        cursor.execute(sql)
        db_status_rows = cursor.fetchall()
        sql_result = dict(db_status_rows)
        conn.close()
    except:
        sql_result = 'mysql connection error'
    finally:
        return sql_result


client = MongoClient(MONITORING_SERVER_IP, MONITORING_SERVER_MONGODB_PORT)
db = client.server_data
coll = db["error_log"]

db_information_logger = logging.getLogger('db_information')
db_information_logger.setLevel(logging.INFO)
db_information_logger.addHandler(
    logstash.LogstashHandler(MONITORING_SERVER_IP, MONITORING_SERVER_DB_INFO_LOGSTASH_PORT, version=1))

uptime_monitoring_client = 0

ip = get_ip_address()
ip_tuple = get_ip_address_tuple()
status_sql_query = 'show global status;'
pre_database_status = ''
database_status = ''
if uptime_monitoring_client == 0:
    pre_database_status = get_result_sql_execute(status_sql_query)
else:
    pre_database_status = database_status

database_status = get_result_sql_execute(status_sql_query)
print(database_status + pre_database_status)