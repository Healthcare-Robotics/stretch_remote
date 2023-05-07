#!/usr/bin/env python3

import sys
import zmq
import json
import threading
import time

# IP_DESKTOP = '143.215.91.191' # TODO: Change this to the IP address of the desktop
# IP_ROBOT = '100.116.230.90' # TODO: Change this to the IP address of the robot

IP_DESKTOP = "192.168.0.39" # '143.215.91.191' # TODO: Change this to the IP address of the desktop
IP_ROBOT = "192.168.0.96"

PORT_COMMAND_SERVER = 5556
PORT_STATUS_SERVER = 5557

class SocketClient:
    def __init__(self, ip, port=5556):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect('tcp://' + ip + ':' + str(port))

        try:    # Needed for python2/3 compatibility
            self.socket.setsockopt(zmq.SUBSCRIBE, b'')
        except TypeError:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, b'')

    def receive_blocking(self):
        payload_string = self.socket.recv_string()
        parsed_dict = json.loads(payload_string)
        return parsed_dict

class SocketThreadedClient(SocketClient):
    def __init__(self, ip, port=5556):
        super().__init__(ip, port)

        self.thread = DaemonStoppableThread(0.001, target=self.poll_socket, name='polling_thread')
        self.thread.start()

        self.last_message = None
        self.last_message_time = 0

    def poll_socket(self):
        self.last_message = self.receive_blocking()
        self.last_message_time = time.time()

    def receive_timeout(self, timeout=1):
        if time.time() - self.last_message_time > timeout:  # if we haven't gotten a valid message in a while
            return None

        return self.last_message

class DaemonStoppableThread(threading.Thread):
    def __init__(self, sleep_time, target=None,  **kwargs):
        super(DaemonStoppableThread, self).__init__(target=target, **kwargs)
        self.setDaemon(True)
        self.stop_event = threading.Event()
        self.sleep_time = sleep_time
        self.target = target

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.isSet()

    def run(self):
        while not self.stopped():
            if self.target:
                self.target()
            else:
                raise Exception('No target function given')
            self.stop_event.wait(self.sleep_time)

if __name__ == "__main__":
    sc = SocketClient()
    while True:
        payload = sc.receive_delta_pos()
        print(payload)
