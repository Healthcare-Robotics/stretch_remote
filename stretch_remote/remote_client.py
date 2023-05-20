#!/usr/bin/env python3

import time
import json
from typing import Dict, List, Optional

from stretch_remote.zmq_wrapper import SocketClient
from stretch_remote.robot_utils import read_robot_status

# Default home dict
HOME_POS_DICT = {
        'x': 0, 'y': 0.1, 'z': 0.75, 'roll': 0, 'pitch': -0.3, 'yaw': 0, 'gripper': 55
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
        
        # related to caching the status
        self.status_poll_limit = 1.0 / 15  # 15 hz limit
        self.cache_status = None # Cache the status and return it if more than 30 hz
        self.latest_poll = time.time()

    def home(self):
        """Robot goes back home"""
        s = json.dumps({"move": self.home_dict, "compact_status": True})
        self.socket_client.send_payload(s)

    def get_status(self,
                   compact=False,
                   return_cache_status=True
                   ) -> Optional[Dict]:
        """
        Get the current status of the robot
        :arg compact: if True, only return compact dict
        :arg cache_status: if True, cache the status to prevent overpolling
        :return: dict of the robot status
        """
        s = json.dumps({"compact_status": compact})
        
        # return cached status if the time is less than the poll limit
        if return_cache_status and \
            time.time() - self.latest_poll < self.status_poll_limit and \
            self.cache_status is not None:
            # TODO: compact and non-compact status cache differently
            return self.cache_status

        s = self.socket_client.send_payload(s)
        if s is None:
            return None

        self.cache_status = json.loads(s)
        self.latest_poll = time.time()
        return json.loads(s)

    def move(self, description: Dict):
        """
        Move the robot by specifying the xyz, rpy, griiper state
        in dict format
        :description: dict desribe the abs joints of the robot
        """
        # print("Moving robot to", description)
        s = json.dumps({"move": description, "compact_status": True})
        self.socket_client.send_payload(s)
