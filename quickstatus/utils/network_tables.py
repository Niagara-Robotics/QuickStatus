import ntcore, struct
from quickstatus.utils.imports import *
from quickstatus.utils.generic import config
from math import degrees

datatable = {
    config['status']['network-table']: {},
    config['swerve']['base-table']: {},
    config['swerve']['wheel-table']: {},
    config['lift']['network-table']: {},
    config['intake']['network-table']: {},
    'SmartDashboard': {}
    }

class NetworkTables():
    inst = ntcore.NetworkTableInstance.getDefault()
    def __init__(self):
        super(NetworkTables, self).__init__()
        inst = NetworkTables.inst
        tables = {}
        tables['status'] = "/" + config['status']['network-table']
        tables['swerve-base'] = config['swerve']['base-table']
        tables['swerve-wheel'] = config['swerve']['wheel-table']
        tables['lift'] = "/" + config['lift']['network-table']
        tables['intake'] = "/" + config['intake']['network-table']
        tables['SmartDashboard'] = "/SmartDashboard"

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
            if isinstance(value, bytes):
                value = struct.unpack(str(int(len(value)/8))+"d", value)
                if len(value) % 2 == 0:
                    temp = []
                    for i in range(0, len(value), 2):
                        temp.append(-degrees(value[i+1]))
                    value = temp
            
            #print(f"({path}) Value updated: {topic} = {value}")
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