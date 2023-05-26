#!/usr/bin/env python3

import time
import json
from typing import Dict, List, Optional

from stretch_remote.zmq_wrapper import SocketClient
from stretch_remote.robot_utils import Schema

# Default home dict
# NOTE: x-axis is not set in DEFAULT HOME as user might drag and 
# move the robot somewhere
HOME_POS_DICT = {
        'y': 0.1, 'z': 0.75, 'roll': 0, 'pitch': -0.3, 'yaw': 0, 'gripper': 55
    }

##############################################################################

class RemoteClient:
    def __init__(self, ip='localhost', port=5556, home_dict=HOME_POS_DICT):
        """
        :arg ip       : IP address of the robot
        :arg port     : Port number of the robot
        :arg home_dict: Home position of the robot
        """
        self.socket_client = SocketClient(ip=ip, port=port)
        self.home_dict = home_dict
        
        # related to caching the status
        poll_freq_limit = 12  # 12 hz limit
        self.status_poll_limit = 1.0 / poll_freq_limit
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
            # NOTE: better way to identify 
            # compact and non-compact status cache differently
            is_compact = "pimu" not in self.cache_status
            if is_compact == compact:
                return self.cache_status

        s = self.socket_client.send_payload(s)
        if s is None:
            return None
        # save the status to cache
        self.cache_status = json.loads(s)
        self.latest_poll = time.time()
        return json.loads(s)

    def move(self, description: Dict) -> Optional[Dict]:
        """
        Move the robot by specifying the xyz, rpy, griiper state
        in dict format
        :description: dict desribe the abs joints of the robot
        :return: dict of the robot status in compact form
        """
        # check if description is a dict
        if not Schema.check_input_schema(description):
            print("[ERROR] Invalid input description provided")
            return None
        s = json.dumps({"move": description, "compact_status": True})
        s = self.socket_client.send_payload(s)
        if s is None:
            return None
        return json.loads(s)
