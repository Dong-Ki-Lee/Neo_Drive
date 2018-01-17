import logstash
import logging
import time
import psutil
import socket


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
# if use intranet only, use host name monitoring server
ip = s.getsockname()[0]
print(ip)
s.close()

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(logstash.LogstashHandler("164.125.14.150", 5959, version=1))


print(psutil.cpu_percent())

network = psutil.net_io_counters().packets_recv
cpu_limit = input("input cpu limit this system : ")
#network_limit = input("input network limit this system : ")
while(True):
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    network_usage = network
    network = psutil.net_io_counters().packets_recv
    network_usage = int((network - network_usage) / 5 / 10240)

    obj = str(cpu) + ' ' + str(mem) + ' ' + str(disk) + ' ' + str(network_usage) + ' ' + cpu_limit + ' ' + ip
    print(obj)
#    psutil.test()
#    test_logger.info(obj)

    print("insert one data")
    time.sleep(1)
