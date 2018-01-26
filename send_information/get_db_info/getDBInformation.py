from pymongo import MongoClient
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

client = MongoClient('164.125.14.151', 26543)
db = client.server_data
coll = db["error_log"]

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.LogstashHandler("164.125.14.150", 5958, version=1))

# normal value
NORMAL = '0'

pre_questions = 0
pre_bytes_sent = 0
pre_bytes_received = 0
pre_created_tmp_disk_tables = 0
pre_connections = 0
pre_handler_read_rnd_next = 0
pre_com_select = 0

uptime_monitoring_client = 0

while True:
    conn = pymysql.connect(host='localhost', user='monitoring', password='monitoringtest', charset='utf8')
    curs = conn.cursor()
    sql = 'show status;'
    curs.execute(sql)
    rows = curs.fetchall()
    status = dict(rows)
    print(rows)
    # initiating
    if uptime_monitoring_client == 0:
        pre_created_tmp_disk_tables = status['Created_tmp_disk_tables']
        pre_bytes_sent = status['Bytes_sent']
        pre_bytes_received = status['Bytes_received']
        pre_questions = status['Questions']
        pre_connections = status['Connections']
        pre_handler_read_rnd_next = status['Handler_read_rnd_next']
        pre_com_select = status['Com_select']
        uptime_monitoring_client += 1
        conn.close()
        time.sleep(60)
        continue

    # Select_full_join
    if status['Select_full_join'] != NORMAL:
        t = time.localtime()
        error_log = {'error_name': "Select_full_join",
                     'error_time': time.asctime(t),
                     'error_ip': ip}
        coll.insert_one(error_log)
        print("Select_full_join error sending")
        select_full_join = status['Select_full_join']
        # send information to mongodb

    # Select_range_check
    if status['Select_range_check'] != NORMAL:
        t = time.localtime()
        error_log = {'error_name': "Select_range_check",
                     'error_time': time.asctime(t),
                     'error_ip': ip}
        coll.insert_one(error_log)
        print("Select_range_check error sending")
        select_range_check = status['Select_range_check']
        # send information to mongodb
    # Send DB status information to logstash

    db_status_information = ()

    bytes_sent_tuple = (('Bytes_sent_per_minute', int(status['Bytes_sent']) - int(pre_bytes_sent)),)
    pre_bytes_sent = status['Bytes_sent']
    db_status_information += bytes_sent_tuple

    questions_per_minute_tuple = (('Questions_per_minute', int(status['Questions']) - int(pre_questions)), )
    pre_questions = status['Questions']
    db_status_information += questions_per_minute_tuple
    try:
        average_sent_per_question_tuple = (('Average_sent_per_question', int(bytes_sent_tuple[0][1])
                                            / int(questions_per_minute_tuple[0][1])), )
    except ZeroDivisionError:
        average_sent_per_question_tuple = 0

    average_sent_per_question_tuple = (('Average_sent_per_question_tuple', average_sent_per_question_tuple), )
    db_status_information += average_sent_per_question_tuple

    disk_access_per_minute_tuple = (('Disk_access_per_minute',
                                     int(status['Created_tmp_disk_tables']) - int(pre_created_tmp_disk_tables)), )
    pre_created_tmp_disk_tables = status['Created_tmp_disk_tables']
    db_status_information += disk_access_per_minute_tuple

    handler_read_rnd_next = int(status['Handler_read_rnd_next']) - int(pre_handler_read_rnd_next)
    com_select = int(status['Com_select']) - int(pre_com_select)
    efficiency_of_index = 0
    if com_select == 0:
        efficiency_of_index = 0
    else:
        efficiency_of_index = handler_read_rnd_next / com_select

    efficiency_of_index_tuple = (('Efficiency_of_index_tuple', int(efficiency_of_index)), )
    db_status_information += efficiency_of_index_tuple

    test_logger.info(db_status_information + ip_tuple)
    print(db_status_information)
    sql = 'show processlist;'
    curs.execute(sql)
    rows = curs.fetchall()
#    test_logger.info(rows)
    conn.close()

    time.sleep(60)



