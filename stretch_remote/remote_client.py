#!/usr/bin/env python3

import json
from typing import Dict, List, Tuple

from stretch_remote.zmq_wrapper import SocketClient

HOME_POS_DICT = {
        'y': 0.1, 'z': 0.75, 'roll': 0, 'pitch': -0.3, 'yaw': 0, 'gripper': 55
    }

##############################################################################

class RemoteClient:
    def __init__(self, ip, port):
        self.socket_client = SocketClient(ip=ip, port=port)
    
    def home(self):
        """Robot goes back home"""
        s = json.dumps(HOME_POS_DICT)
        self.socket_client.send_payload(s)

    def get_status(self) -> Dict:
        """Get the current status of the robot"""
        s = self.socket_client.send_payload("")
        return json.loads(s)

    def move(self, description: Dict):
        """
        Move the robot by specifying the xyz, rpy, griiper state in dict format
        """
        # print("Moving robot to", description)
        s = json.dumps(description)
        self.socket_client.send_payload(s)
