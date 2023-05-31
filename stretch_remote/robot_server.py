#!/usr/bin/env python3

import argparse
import stretch_body.robot

from stretch_remote.robot_utils import read_robot_status
from stretch_remote.zmq_wrapper import SocketServer

from typing import Dict, List, Tuple
import json

##############################################################################
class RobotControlServer:
    def __init__(self, port, speed_factor=1.0):
        self.robot = stretch_body.robot.Robot()
        self.robot.startup()

        self.arm_vel = 0.2 * speed_factor
        self.arm_accel = 0.2 * speed_factor

        self.base_vel = 0.2 * speed_factor
        self.base_accel = 0.2 * speed_factor

        # NOTE: the wrist velocity are not actually working
        self.wrist_vel = 25 * speed_factor
        self.wrist_accel = 15 * speed_factor

        self.socker_server = SocketServer(port=port,
                                          impl_callback=self.__request_callback)

    def publish_status_loop(self):
        status = self.robot.get_status()
        self.server.send_payload(status)

    def __request_callback(self, request):
        json_dict = json.loads(request)
        if "move" in json_dict:
            self.navigate_robot_abs(json_dict["move"])

        s = self.robot.get_status()
        if "compact_status" in json_dict and json_dict["compact_status"]:
            s = read_robot_status(s)

        status = json.dumps(s)
        return status.encode()

    def navigate_robot_abs(self, input_dict: Dict):
        print('Lift force', self.robot.lift.status['force'])
        # Since the robot base api only supports relative movement, we need to
        # calculate the relative movement and then move the robot base
        if 'x' in input_dict:
            delta_x = input_dict['x'] - self.robot.base.status['x']
            self.robot.base.translate_by(delta_x, self.arm_vel, self.arm_accel)
        elif 'delta_x' in input_dict:
            self.robot.base.translate_by(input_dict['delta_x'], self.base_vel, self.base_accel)
        elif 'delta_rz' in input_dict:
            self.robot.base.translate_by(input_dict['delta_rz'])

        if 'y' in input_dict:
            self.robot.arm.move_to(input_dict['y'], self.arm_vel, self.arm_accel)
        if 'z' in input_dict:
            self.robot.lift.move_to(input_dict['z'], self.arm_vel, self.arm_accel)
        if 'roll' in input_dict:
            self.robot.end_of_arm.move_to(
                'wrist_roll', input_dict['roll'], self.wrist_vel, self.wrist_accel)
        if 'pitch' in input_dict:
            self.robot.end_of_arm.move_to(
                'wrist_pitch', input_dict['pitch'], self.wrist_vel, self.wrist_accel)
        if 'yaw' in input_dict:
            self.robot.end_of_arm.move_to(
                'wrist_yaw', input_dict['yaw'], self.wrist_vel, self.wrist_accel)
        if 'gripper' in input_dict:
            # print('moving gripper to ', input_dict['gripper'])
            self.robot.end_of_arm.move_to(
                'stretch_gripper', input_dict['gripper'], self.wrist_vel, self.wrist_accel)
        self.robot.push_command()

    def run(self):
        self.socker_server.run()

##############################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5556)
    parser.add_argument('-s', '--speed', type=float, default=1.0,
                        help='speed factor of the robot (default: 1.0)')
    args = parser.parse_args()

    sm = RobotControlServer(port=args.port, speed_factor=args.speed)
    sm.run()
