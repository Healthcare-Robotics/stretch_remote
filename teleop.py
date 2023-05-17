#!/usr/bin/env python3

import argparse
import sys
import select
import tty
import termios
import json
from typing import Dict, List, Tuple
from stretch_remote.robot_utils import *
import signal

from stretch_remote.remote_client import RemoteClient

def get_robot_status(client: RemoteClient):
    """
    Get the current status of the robot from RemoteClient class
    """
    _robot_status = client.get_status()
    if _robot_status is not None:
        pos_dict = read_robot_status(_robot_status)
        return pos_dict
    return None

def teleop(client: RemoteClient):
    """
    Drive the robot with the keyboard
    """
    print(
        """
        Quit by pressing 'q'
        
        Instructions:
            [ ] : drive X
            a d : drive Y
            x w : drive Z
            u o : drive roll
            , i : drive pitch
            j l : drive yaw
            b n : drive gripper
            space : toggle moving
        """
    )
    delta_lin = 0.01
    delta_ang = 0.1
    enable_moving = True

    # Put the console in raw mode
    original_settings = termios.tcgetattr(sys.stdin)
    tty.setraw(sys.stdin.fileno())

    do_loop = True
    pos_dict = get_robot_status(client)
    if pos_dict is None:
        print("Robot is not connected, exiting...")
        do_loop = False

    while do_loop:
        # Get keyboard input
        input_ready, _, _ = select.select([sys.stdin], [], [], 0.1)

        # # If input is ready, read it from the keyboard and do something with it
        if not sys.stdin in input_ready:
            continue
        keycode  = sys.stdin.read(1)

        # print("Input received:", input_char, "\n")
        _robot_status = client.get_status()
        if _robot_status is not None:
            pos_dict = read_robot_status(_robot_status)
        # print("Current position:", pos_dict)

        if keycode == ' ':     # toggle moving
            enable_moving = not enable_moving
        elif keycode == 'h':     # go home
            enable_moving = False
            client.home()
        if enable_moving:
            if keycode == 'q':
                print("Exiting")
                break
            elif keycode == '[':     # drive X
                client.move({'delta_x':delta_lin})
            elif keycode == ']':     # drive X
                client.move({'delta_x':delta_lin})
            elif keycode == 'a':     # drive Y
                client.move({'y':pos_dict['y'] - delta_lin})
            elif keycode == 'd':     # drive Y
                client.move({'y':pos_dict['y'] + delta_lin})
            elif keycode == 'x':     # drive Z
                client.move({'z':pos_dict['z'] - delta_lin})
            elif keycode == 'w':     # drive Z
                client.move({'z':pos_dict['z'] + delta_lin})
            elif keycode == 'u':     # drive roll
                client.move({'roll':pos_dict['roll'] - delta_ang})
            elif keycode == 'o':     # drive roll
                client.move({'roll':pos_dict['roll'] + delta_ang})
            elif keycode == ',':     # drive pitch
                client.move({'pitch':pos_dict['pitch'] - delta_ang})
            elif keycode == 'i':     # drive pitch
                client.move({'pitch':pos_dict['pitch'] + delta_ang})
            elif keycode == 'j':     # drive yaw
                client.move({'yaw':pos_dict['yaw'] - delta_ang / 2})
            elif keycode == 'l':     # drive yaw
                client.move({'yaw':pos_dict['yaw'] + delta_ang / 2})
            elif keycode == 'b':     # drive gripper
                # print("Gripper position:", pos_dict['gripper'])
                client.move({'gripper':pos_dict['gripper'] - 5})
            elif keycode == 'n':     # drive gripper
                client.move({'gripper':pos_dict['gripper'] + 5})

    # Restore the console to its original settings
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)
    print("Done Exiting")

##############################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Remote control for Stretch')
    parser.add_argument('--ip', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=5556)
    args = parser.parse_args()
    rc = RemoteClient(ip=args.ip, port=args.port)
    teleop(rc)
