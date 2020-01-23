from websockets import socketio
from threading import Thread, Event
from time import sleep
from helper import convert_bytes
import psutil
import socket
import os

thread = Thread()
thread_stop_event = Event()

class DynamicData(Thread):
    
    def __init__(self):
        self.delay = 1
        self.af_map = {
                socket.AF_INET: 'IPv4',
                socket.AF_INET6: 'IPv6',
                psutil.AF_LINK: 'MAC',
                }
        self.data = {
            'CPU' : {
                'Usage' : 0.0,
                'Frequency' : 0.0,
            },
            'Memory' : {
                'Usage' : '',
                'Used' : '',
                'Avail' : '',
                'Total' : '',
                },
           'SwapMemory' : {
                'Usage' : '',
                'Used' : '',
                'Avail' : '',
                'Total' : '',
                },
 
            'Disk' : {},
            'Network' : {},
        }
        super(DynamicData, self).__init__()

    def updateDynamicData(self):
        self.data['CPU']['Usage'] = psutil.cpu_percent();
        self.data['CPU']['Frequency'] = psutil.cpu_freq().current;
        self.data['Memory']['Usage'] = psutil.virtual_memory().percent;
        self.data['Memory']['Used'] = convert_bytes(psutil.virtual_memory().percent);
        self.data['Memory']['Avail'] = convert_bytes(psutil.virtual_memory().available);
        self.data['Memory']['Total'] = convert_bytes(psutil.virtual_memory().total);

        self.data['SwapMemory']['Usage'] = psutil.swap_memory().percent;
        self.data['SwapMemory']['Used'] = convert_bytes(psutil.swap_memory().used);
        self.data['SwapMemory']['Avail'] = convert_bytes(psutil.swap_memory().free);
        self.data['SwapMemory']['Total'] = convert_bytes(psutil.swap_memory().total);

        for part in psutil.disk_partitions():
            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '':
                    continue
            usage = psutil.disk_usage(part.mountpoint)
            self.data['Disk'][part.device] = {
                'Total' : convert_bytes(usage.total),
                'Used' : convert_bytes(usage.used),
                'Free' : convert_bytes(usage.free),
                'Usage' : usage.percent,
                'Type' : part.fstype,
                'Mount' : part.mountpoint,
                    }

        io_counters = psutil.net_io_counters(pernic=True)
        for nic, addrs in psutil.net_if_addrs().items():
            if nic in io_counters:
                io = io_counters[nic]
                incoming = convert_bytes(io.bytes_recv)
                outgoing = convert_bytes(io.bytes_sent)
            else:
                incoming = ''
                outgoing = ''

            self.data['Network'][nic] = {
                'Incoming' : incoming,
                'Outgoing' : outgoing,
                    }

            for addr in addrs:
                if addr.broadcast:
                    broadcast = addr.broadcast
                else:
                    broadcast = ''
                if addr.netmask:
                    netmask = addr.netmask
                else:
                    netmask = ''

                self.data['Network'][nic][self.af_map.get(addr.family, addr.family)] = {
                        'Address' : addr.address,
                        'Broadcast' : broadcast,
                        'Netmask' : netmask,
                        }


    def emitDynamicData(self):

        while not thread_stop_event.isSet():
            self.updateDynamicData();
            socketio.emit('dynamic_system_data', self.data)
            sleep(self.delay)


    def run(self):
        self.emitDynamicData()

class StaticData(Thread):

    def __init__(self):
        self.delay = 1
        self.data = {
            'CPU' : {
                'min_freq' : 0.0,
                'max_freq' : 0.0,
            }
        }

    def updateStaticData(self):
        self.data = {
            'CPU' : {
                'min_freq' : psutil.cpu_freq().min,
                'max_freq' : psutil.cpu_freq().max,
            }
        }

    def emitStaticData(self):

        self.updateStaticData()
        socketio.emit('static_system_data', self.data)

    def run(self):
        self.emitStaticData()

