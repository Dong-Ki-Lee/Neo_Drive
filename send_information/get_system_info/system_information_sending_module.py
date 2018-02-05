import logstash
import logging
import time
import psutil
import socket
from pymongo import MongoClient


MONITORING_SERVER_IP = '164.125.14.150'
MONITORING_SERVER_MONGODB_PORT = 26543
MONITORING_SERVER_SYSTEM_INFO_LOGSTASH_PORT = 5959
MONITORING_SERVER_ERROR_INFO_LOGSTASH_PORT = 5957


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    # if use intranet only, use host name monitoring server
    ip = s.getsockname()[0]
    s.close()
    return ip


def insert_data_in_mongodb(coll_name, json_data):
    is_success = 1
    try:
        client = MongoClient(MONITORING_SERVER_IP, MONITORING_SERVER_MONGODB_PORT)
        db = client.server_data
        collection = db[coll_name]
        collection.insert_one(json_data)
        client.close()
    except:
        is_success = 0
    finally:
        return is_success


system_information_logger = logging.getLogger('system_information_logger')
system_information_logger.setLevel(logging.INFO)
system_information_logger.addHandler(logstash.LogstashHandler(
    MONITORING_SERVER_IP,
    MONITORING_SERVER_SYSTEM_INFO_LOGSTASH_PORT,
    version=1)
)

system_error_logger = logging.getLogger('error_logger')
system_error_logger.setLevel(logging.INFO)
system_error_logger.addHandler(logstash.LogstashHandler(
    MONITORING_SERVER_IP,
    MONITORING_SERVER_ERROR_INFO_LOGSTASH_PORT,
    version=1)
)

network = psutil.net_io_counters().packets_recv
cpu_usage_limit = input("input cpu usage limit this system : ")
cpu_time_limit = input("input cpu time limit this system : ")

cpu_over_limit_time = 0
ip = get_ip_address()
client_information = {
    'IP': ip,
    'type': 'connect',
    'access_time': time.asctime(time.localtime())
}

insert_data_in_mongodb("access_log", client_information)

while(True):
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    network_usage = network
    network = psutil.net_io_counters().packets_recv
    network_usage = int((network - network_usage) / 5 / 10240)

    system_information = str(cpu) + ' ' + str(mem) + ' ' + str(disk) + ' ' + str(network_usage) + ' ' + cpu_usage_limit + ' ' + ip
    print(system_information)
#    psutil.test()
    system_information_logger.info(system_information)

    print("insert one data")

    if int(cpu) > int(cpu_usage_limit):
        if int(cpu_over_limit_time) < int(cpu_time_limit):
            cpu_over_limit_time += 1
        else:
            t = time.localtime()
            error_information = {
                'error_name': 'CPU_Usage_over_limit',
                'error_time': time.asctime(t),
                'error_ip': ip
            }

            insert_data_in_mongodb("error_log", error_information)

            elastic_obj = ip + ' ' + 'CPU_Usage_over_limit'
            system_error_logger.info(elastic_obj)
            print("send cpu limit error")
            cpu_over_limit_time = 0
    else:
        cpu_over_limit_time = 0

    print("cpu over limit count : " + str(cpu_over_limit_time))
    time.sleep(5)
