#!/usr/bin/env python3

import json
from typing import Dict, List, Optional

from stretch_remote.zmq_wrapper import SocketClient
from stretch_remote.robot_utils import read_robot_status

# Default home dict
HOME_POS_DICT = {
        'y': 0.1, 'z': 0.75, 'roll': 0, 'pitch': -0.3, 'yaw': 0, 'gripper': 55
    }

##############################################################################

class RemoteClient:
    def __init__(self, ip, port=5556, home_dict=HOME_POS_DICT):
        """
        :arg ip       : IP address of the robot
        :arg port     : Port number of the robot
        :arg home_dict: Home position of the robot
        """
        self.socket_client = SocketClient(ip=ip, port=port)
        self.home_dict = home_dict

    def home(self):
        """Robot goes back home"""
        s = json.dumps(self.home_dict)
        self.socket_client.send_payload(s)

    def get_status(self, compact=False) -> Optional[Dict]:
        """
        Get the current status of the robot
        :arg compact: if True, only return compact dict
        """
        s = json.dumps({"compact_status": compact})
        s = self.socket_client.send_payload(s)
        if s is None:
            return None
        return json.loads(s)

    def move(self, description: Dict):
        """
        Move the robot by specifying the xyz, rpy, griiper state in dict format
        """
        # print("Moving robot to", description)
        s = json.dumps({"move": description})
        self.socket_client.send_payload(s)
