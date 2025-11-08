#!/usr/bin/env python3
from prometheus_client import start_http_server, Gauge
import psutil
import time
import socket
import requests
import platform
import os

# ==============================
# Define Prometheus Gauges
# ==============================
CPU_USAGE = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('system_memory_usage_percent', 'Memory usage percentage')
DISK_USAGE = Gauge('system_disk_usage_percent', 'Disk usage percentage')
UPTIME = Gauge('system_uptime_seconds', 'System uptime in seconds')
NETWORK_SENT = Gauge('system_network_bytes_sent', 'Network bytes sent')
NETWORK_RECV = Gauge('system_network_bytes_received', 'Network bytes received')
PORT_STATUS = Gauge('service_port_up', 'Port up status (1=up,0=down)', ['port'])
PROCESS_STATUS = Gauge('process_up', 'Process running (1=up,0=down)', ['process'])
URL_STATUS = Gauge('url_up', 'Website availability (1=up,0=down)', ['url'])

# ==============================
# Helper Functions
# ==============================
def check_port(host='localhost', port=80):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        s.close()
        return True
    except:
        return False

def check_process(name):
    for proc in psutil.process_iter(['name']):
        if name.lower() in proc.info['name'].lower():
            return True
    return False

def check_url(url):
    try:
        r = requests.get(url, timeout=3)
        return r.status_code == 200
    except:
        return False

# ==============================
# Metric Collector
# ==============================
def collect_metrics():
    # System
    CPU_USAGE.set(psutil.cpu_percent(interval=1))
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    DISK_USAGE.set(psutil.disk_usage('/').percent)
    UPTIME.set(time.time() - psutil.boot_time())

    net = psutil.net_io_counters()
    NETWORK_SENT.set(net.bytes_sent)
    NETWORK_RECV.set(net.bytes_recv)

    # Service checks
    for port in [22, 80, 443, 9090]:  # example ports
        PORT_STATUS.labels(port=str(port)).set(1 if check_port('localhost', port) else 0)

    for pname in ['nginx', 'sshd', 'prometheus']:
        PROCESS_STATUS.labels(process=pname).set(1 if check_process(pname) else 0)

    for url in ['https://google.com', 'https://github.com']:
        URL_STATUS.labels(url=url).set(1 if check_url(url) else 0)

# ==============================
# Main
# ==============================
if __name__ == '__main__':
    print("Starting Ubuntu Metrics Exporter on port 8000...")
    start_http_server(8000)  # Prometheus will scrape this
    while True:
        collect_metrics()
        time.sleep(10)
