from quickstatus.utils.imports import *
from networktables import NetworkTables as nt
from quickstatus.utils.generic import full_faults, global_config
from math import degrees
import struct

global_config.load()
config = global_config.data

try: datatable = {
    config['faults']['network-table']: {},
    config['swerve']['base-table']: {},
    config['swerve']['wheel-table']: {},
    config['lift']['network-table']: {},
    config['lift']['gripper-table']: {},
    config['intake']['network-table']: {},
    }
except: datatable = {}

class NetworkTables():
    inst = nt.getDefault()
    def __init__(self):
        super(NetworkTables, self).__init__()
        inst = NetworkTables.inst

        inst.setNetworkIdentity("QuickStatus")

        tables = {}
        tables['faults'] = config['faults']['network-table']
        tables['swerve-base'] = config['swerve']['base-table']
        tables['swerve-wheel'] = config['swerve']['wheel-table']
        tables['lift'] = config['lift']['network-table']
        tables['gripper'] = config['lift']['gripper-table']
        tables['intake'] = config['intake']['network-table']
        for i in tables: tables[i] = "/" + tables[i]

        address = config['network']['address']
        if config['network']['ds-client']: inst.startDSClient()
        elif address is not None: inst.initialize(server=address)

        def value_updated(key, value, isNew):
            global datatable
            
            path = key.split("/")
            if "" in path: path.remove("")
            topic = path[-1]
            path = path[0]
            
            # properly read structs and stuff
            if isinstance(value, bytes) and len(value)%8 == 0:
                value = struct.unpack(str(int(len(value)/8))+"d", value)
                if len(value) % 2 == 0:
                    temp = []
                    for i in range(0, len(value), 2):
                        temp.append(-degrees(value[i+1]))
                    value = temp
            
            # properly read faults
            if topic.endswith('_faults'):
                faults = value.split(',')[:-1]
                for i in faults:
                    value = []
                    value.append(full_faults[i])
            
            #print(f"({path}) Value updated: {topic} = {value}")
            if path in datatable: datatable[path][topic] = value

        def connected(connected, conn_info):
            if connected:
                print(f"NetworkTables connected ({conn_info.remote_ip}: {conn_info.remote_port})")
            else:
                print(f"NetworkTables disconnnected ({conn_info.remote_ip}: {conn_info.remote_port})")

        inst.addEntryListener(value_updated, True)
        inst.addConnectionListener(connected, True)
