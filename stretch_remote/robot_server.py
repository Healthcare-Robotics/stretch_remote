#!/usr/bin/env python3

import argparse
import stretch_body.robot
from stretch_remote.zmq_wrapper import SocketServer
from typing import Dict, List, Tuple
import json

##############################################################################
class RobotControlServer:
    def __init__(self, port):
        self.robot = stretch_body.robot.Robot()
        self.robot.startup()

        self.arm_vel = 0.15
        self.arm_accel = 0.15

        self.wrist_vel = 0.000000001 
        self.wrist_accel = 0.0000000001

        self.socker_server = SocketServer(port=port,
                                          impl_callback=self.__request_callback)

    def publish_status_loop(self):
        status = self.robot.get_status()
        self.server.send_payload(status)

    def __request_callback(self, request):
        if request:
            json_dict = json.loads(request)
            self.navigate_robot_abs(json_dict)
        status = json.dumps(self.robot.get_status())
        return status.encode()

    def navigate_robot_abs(self, input_dict: Dict):
        print('Lift force', self.robot.lift.status['force'])
        if 'x' in input_dict:
            self.robot.base.translate_by(input_dict['x'], self.arm_vel, self.arm_accel)
        if 'y' in input_dict:
            self.robot.arm.move_to(input_dict['y'], self.arm_vel, self.arm_accel)
        if 'z' in input_dict:
            self.robot.lift.move_to(input_dict['z'], self.arm_vel, self.arm_accel)
        if 'roll' in input_dict:
            self.robot.end_of_arm.move_to('wrist_roll', input_dict['roll'], self.wrist_vel, self.wrist_accel)
        if 'pitch' in input_dict:
            self.robot.end_of_arm.move_to('wrist_pitch', input_dict['pitch'], self.wrist_vel, self.wrist_accel)
        if 'yaw' in input_dict:
            self.robot.end_of_arm.move_to('wrist_yaw', input_dict['yaw'], self.wrist_vel, self.wrist_accel)
        if 'gripper' in input_dict:
            print('moving gripper to ', input_dict['gripper'])
            self.robot.end_of_arm.move_to('stretch_gripper', input_dict['gripper'], self.wrist_vel, self.wrist_accel)
        self.robot.push_command()
        
    def run(self):
        self.socker_server.run()

##############################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5556)
    args = parser.parse_args()

    sm = RobotControlServer(port=args.port)
    sm.run()
