#!/usr/bin/env python3

import zmq
import argparse

##############################################################################

class SocketServer:
    def __init__(self, port=5556, impl_callback=None):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{port}")
        self.impl_callback = impl_callback
        print("Socket server is listening...")

    def run(self):
        while True:
            #  Wait for next request from client
            message = self.socket.recv()
            print(f"Received request: {message}")
            #  Send reply back to client
            
            if self.impl_callback:
                res = self.impl_callback(message)
                self.socket.send(res)
            else:
                print("WARNING: No implementation callback provided.")
                self.socket.send(b"World")

##############################################################################

class SocketClient:    
    def __init__(self, ip, port=5556):
        self.context = zmq.Context()
        #  Socket to talk to server
        print("Connecting to socket server…")
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{ip}:{port}")

    def send_payload(self, request):
        # print(f"Sending request {request} …")
        encoded_str = request.encode()
        self.socket.send(encoded_str)
        # Get the reply.
        message = self.socket.recv()
        # print(f"Received reply {request} [ {message} ]")
        return message


##############################################################################

if __name__ == "__main__":
    # NOTE: This is just for Testing
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--client', action='store_true')
    parser.add_argument('--ip', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=5556)
    args = parser.parse_args()

    if args.server:
        ss = SocketServer(port=args.port)
        ss.run()
    elif args.client:
        sc = SocketClient(ip=args.ip, port=args.port)
        sc.send_payload('hello')
    else:
        raise Exception('Must specify --server or --client')
