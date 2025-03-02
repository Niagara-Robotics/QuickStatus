import ntcore, struct
from time import sleep
from utils.imports import *
from utils.generic import config
from math import degrees

datatable = {
    config['status']['network-table']: {},
    config['swerve']['base-table']: {},
    config['swerve']['wheel-table']: {}
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
        #tables['claw'] = inst.getTable(config['claw']['network-table'])

        address = config['network']['address']
        if isinstance(address, str): inst.setServer(address)
        elif isinstance(address, int): inst.setServerTeam(address)
        if config['network']['ds-client']: inst.startDSClient()
        else: inst.startClient4("QuickStatus")

        def value_updated(event):
            global datatable
            path = event.data.topic.getName().split("/")
            path.pop(-1)
            path = "".join(path)
            topic = event.data.topic.getName().split("/")[-1]
            value = event.data.value.value()

            if isinstance(value, bytes):
                value = struct.unpack(str(int(len(value)/8))+"d", value)
                if len(value) % 2 == 0:
                    temp = []
                    for i in range(0, len(value), 2):
                        temp.append(-degrees(value[i+1]))
                    value = temp
            #print(f"({path}) Value updated: {topic} = {value}")
            datatable[path][topic] = value
        
        def topic_removed(event):
            global datatable
            path = event.data.topic.getName().split("/")
            path.pop(-1)
            path = "".join(path)
            topic = event.data.topic.getName().split("/")[-1]
            inst.getTable("fart").getNumber
            #print(f"({path}) Topic removed: {topic}")
            datatable[path].pop(topic)

        def connected(event):
            if inst.isConnected():
                print(f"NetworkTables connected ({event.data.remote_ip}: {event.data.remote_port})")
            else:
                print(f"NetworkTables disconnnected ({event.data.remote_ip}: {event.data.remote_port})")

        self.topicAddedListeners = []
        self.topicRemovedListeners = []
        for i in tables:
            self.topicAddedListeners.append (inst.addListener(
                [tables[i] + "/"], ntcore.EventFlags.kValueAll, value_updated
            ))
            self.topicRemovedListeners.append (inst.addListener(
                [tables[i] + "/"], ntcore.EventFlags.kUnpublish, topic_removed
            ))

        self.connectedListener = inst.addConnectionListener(True, connected)