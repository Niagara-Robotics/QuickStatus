import ntcore, struct
from quickstatus.utils.imports import *
from quickstatus.utils.generic import full_faults, global_config
from math import degrees

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
    inst = ntcore.NetworkTableInstance.getDefault()
    def __init__(self):
        super(NetworkTables, self).__init__()
        inst = NetworkTables.inst

        tables = {}
        tables['faults'] = config['faults']['network-table']
        tables['swerve-base'] = config['swerve']['base-table']
        tables['swerve-wheel'] = config['swerve']['wheel-table']
        tables['lift'] = config['lift']['network-table']
        tables['gripper'] = config['lift']['gripper-table']
        tables['intake'] = config['intake']['network-table']
        for i in tables: tables[i] = "/" + tables[i]

        address = config['network']['address']
        if isinstance(address, str): inst.setServer(address)
        elif isinstance(address, int): inst.setServerTeam(address)
        if config['network']['ds-client']: inst.startDSClient()
        inst.startClient4("QuickStatus")

        def value_updated(event):
            global datatable
            path = event.data.topic.getName().split("/")
            if "" in path: path.remove("")
            path = path[0]
            topic = event.data.topic.getName().split("/")[-1]
            value = event.data.value.value()
            
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
                    value.append(full_faults[(i)])
            
            print(f"({path}) Value updated: {topic} = {value}")
            datatable[path][topic] = value

        def connected(event):
            if inst.isConnected():
                print(f"NetworkTables connected ({event.data.remote_ip}: {event.data.remote_port})")
            else:
                print(f"NetworkTables disconnnected ({event.data.remote_ip}: {event.data.remote_port})")

        self.topicAddedListeners = []
        for i in tables:
            self.topicAddedListeners.append(inst.addListener(
                [tables[i] + "/"], ntcore.EventFlags.kValueAll, value_updated
            ))

        self.connectedListener = inst.addConnectionListener(True, connected)