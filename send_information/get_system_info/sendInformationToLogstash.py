import logstash
import logging
import time
import psutil
import socket
from pymongo import MongoClient

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
# if use intranet only, use host name monitoring server
ip = s.getsockname()[0]
print(ip)
s.close()

client = MongoClient('164.125.14.150', 26543)
db = client.client_system_limit_error
db_information = client.client_access_log

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.LogstashHandler("164.125.14.150", 5959, version=1))


print(psutil.cpu_percent())

network = psutil.net_io_counters().packets_recv
cpu_usage_limit = input("input cpu usage limit this system : ")
cpu_time_limit = input("input cpu time limit this system : ")
#network_limit = input("input network limit this system : ")

cpu_over_limit_time = 0

coll_information = db_information["access_log"]
client_information = {
    'IP': ip,
    'access_time': time.asctime(time.localtime())
}
coll_information.insert_one(client_information)

while(True):
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    network_usage = network
    network = psutil.net_io_counters().packets_recv
    network_usage = int((network - network_usage) / 5 / 10240)

    obj = str(cpu) + ' ' + str(mem) + ' ' + str(disk) + ' ' + str(network_usage) + ' ' + cpu_usage_limit + ' ' + ip
    print(obj)
#    psutil.test()
    test_logger.info(obj)

    print("insert one data")

    if int(cpu) > int(cpu_usage_limit):
        if int(cpu_over_limit_time) < int(cpu_time_limit):
            cpu_over_limit_time += 1
        else:
            coll = db["cpu_over_limit"]
            t = time.localtime()
            obj = {
                'IP': ip,
                'occur_time': time.asctime(t),
                'error_name': 'CPU Usage over limit'
            }
            coll.insert_one(obj)
            print("send cpu limit error")
            cpu_over_limit_time = 0
    else:
        cpu_over_limit_time = 0

    print("cpu over limit count : " + str(cpu_over_limit_time))
    time.sleep(5)
