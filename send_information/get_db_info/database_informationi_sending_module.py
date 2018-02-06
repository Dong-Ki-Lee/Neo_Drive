from pymongo import MongoClient
import pymysql
import logstash
import logging
import time
import socket

MONITORING_SERVER_IP = '164.125.14.150'
MONITORING_SERVER_MONGODB_PORT = 26543
MONITORING_SERVER_DB_INFO_LOGSTASH_PORT = 5958
MONITORING_SERVER_ERROR_INFO_LOGSTASH_PORT = 5957

# Database ID and Password
DATABASE_ID = 'monitoring'
DATABASE_PW = 'monitoringtest'
# normal value
NORMAL = 0

system_error_logger = logging.getLogger('error_logger')
system_error_logger.setLevel(logging.INFO)
system_error_logger.addHandler(logstash.LogstashHandler(
    MONITORING_SERVER_IP,
    MONITORING_SERVER_ERROR_INFO_LOGSTASH_PORT,
    version=1)
)

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


def insert_data_in_mongodb(json_data):
    is_success = 1
    try:
        client = MongoClient(MONITORING_SERVER_IP, MONITORING_SERVER_MONGODB_PORT)
        db = client.server_data
        coll = db["error_log"]
        coll.insert_one(json_data)
        client.close()
    except:
        is_success = 0
    finally:
        return is_success


def database_error_check(pre_database_status, database_status):

    # Select_full_join
    select_full_join = int(database_status['Select_full_join']) - int(pre_database_status['Select_full_join'])
    if select_full_join != NORMAL:

        # send information to mongodb
        t = time.localtime()

        error_log = {'error_name': "Select_full_join",
                     'error_time': time.asctime(t),
                     'error_ip': ip}

        insert_data_in_mongodb(error_log)
        print("Select_full_join error sending")

        # send information to logstash
        elastic_obj = ip + ' ' + 'Select_full_join'
        system_error_logger.info(elastic_obj)
        print("send cpu limit error")


    # Select_range_check
    select_range_check = int(database_status['Select_range_check']) - int(pre_database_status['Select_range_check'])
    if select_range_check != NORMAL:

        # send information to mongodb
        t = time.localtime()

        error_log = {'error_name': "Select_range_check",
                     'error_time': time.asctime(t),
                     'error_ip': ip}

        insert_data_in_mongodb(error_log)
        print("Select_range_check error sending")

        # send information to logstash
        elastic_obj = ip + ' ' + 'Select_range_check'
        system_error_logger.info(elastic_obj)
        print("send cpu limit error")



db_information_logger = logging.getLogger('db_information')
db_information_logger.setLevel(logging.INFO)
db_information_logger.addHandler(
    logstash.LogstashHandler(
        MONITORING_SERVER_IP,
        MONITORING_SERVER_DB_INFO_LOGSTASH_PORT,
        version=1
    )
)


uptime_monitoring_client = 0

ip = get_ip_address()
ip_tuple = get_ip_address_tuple()

pre_database_status = ''
database_status = ''

while True:
    status_sql_query = 'show global status;'
    if uptime_monitoring_client == 0:
        pre_database_status = get_result_sql_execute(status_sql_query)
    else:
        pre_database_status = database_status

    time.sleep(60)

    database_status = get_result_sql_execute(status_sql_query)
    print(database_status)
    database_error_check(pre_database_status, database_status)
    # Send DB status information to logstash

    db_status_information = ()

    bytes_sent_tuple = (('Bytes_sent_per_minute',
                         int(database_status['Bytes_sent']) - int(pre_database_status['Bytes_sent'])),)

    db_status_information += bytes_sent_tuple

    questions_per_minute_tuple = (('Questions_per_minute',
                                   int(database_status['Questions']) - int(pre_database_status['Questions'])),)

    db_status_information += questions_per_minute_tuple

    average_sent_per_question = 0
    try:
        average_sent_per_question = int(int(bytes_sent_tuple[0][1]) / int(questions_per_minute_tuple[0][1]))
    except ZeroDivisionError:
        average_sent_per_question = 0

    average_sent_per_question_tuple = (('Average_sent_per_question', average_sent_per_question),)

    db_status_information += average_sent_per_question_tuple

    disk_access_per_minute_tuple = (('Disk_access_per_minute',
                                     int(database_status['Created_tmp_disk_tables'])
                                     - int(pre_database_status['Created_tmp_disk_tables'])),)

    db_status_information += disk_access_per_minute_tuple

    handler_read_rnd_next = \
        int(database_status['Handler_read_rnd_next']) \
        - int(pre_database_status['Handler_read_rnd_next'])
    com_select = int(database_status['Com_select']) - int(pre_database_status['Com_select'])

    efficiency_of_index = 0
    if com_select == 0:
        efficiency_of_index = 0
    else:
        efficiency_of_index = handler_read_rnd_next / com_select

    efficiency_of_index_tuple = (('Efficiency_of_index_tuple', int(efficiency_of_index)), )

    db_status_information += efficiency_of_index_tuple

    select_tuple = (('Select',
                     int(database_status['Com_select']) - int(pre_database_status['Com_select'])),)
    db_status_information += select_tuple
    insert_tuple = (('Insert',
                     int(database_status['Com_insert']) - int(pre_database_status['Com_insert'])),)
    db_status_information += insert_tuple
    update_tuple = (('Update',
                     int(database_status['Com_update']) - int(pre_database_status['Com_update'])),)
    db_status_information += update_tuple
    delete_tuple = (('Delete',
                     int(database_status['Com_delete']) - int(pre_database_status['Com_delete'])),)
    db_status_information += delete_tuple

    innodb_buffer_pool_reads = int(database_status['Innodb_buffer_pool_reads']) \
                               - int(pre_database_status['Innodb_buffer_pool_reads'])

    innodb_buffer_pool_read_requests = int(database_status['Innodb_buffer_pool_read_requests']) \
                                       - int(pre_database_status['Innodb_buffer_pool_read_requests'])

    cache_rate = 0
    if innodb_buffer_pool_read_requests == 0:
        cache_rate = 0
    else:
        cache_rate = innodb_buffer_pool_reads * 100 / innodb_buffer_pool_read_requests

        cache_rate_tuple = (('Cache_rate', int(cache_rate)), )

    db_status_information += cache_rate_tuple

    data_written_tuple = (('Data_written',
                           (int(database_status['Innodb_data_written'])
                            - int(pre_database_status['Innodb_data_written']))/1024),)
    db_status_information += data_written_tuple

    data_read_tuple = (('Data_read',
                           (int(database_status['Innodb_data_read'])
                            - int(pre_database_status['Innodb_data_read']))/1024),)
    db_status_information += data_read_tuple

    db_status_information += ip_tuple

    db_information_logger.info(db_status_information)
    print(db_status_information)
    status_sql_query = 'show processlist;'

    uptime_monitoring_client += 1



