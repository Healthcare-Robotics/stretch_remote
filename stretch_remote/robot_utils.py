#!/usr/bin/env python3

class Schema:
    SCHEMA_DEF = {
        'x': float,
        'y': float,
        'z': float,
        'roll': float,
        'pitch': float,
        'yaw': float,
        'gripper': float,
    }

    @staticmethod
    def check_input_schema(data):
        if not isinstance(data, dict):
            print("Input must be a dict")
            return False
        for key in data.keys():
            if key not in Schema.SCHEMA_DEF:
                print(f'Unknown key "{key}" provided.')
                return False
            if Schema.SCHEMA_DEF[key] == float and isinstance(data[key], int):
                # allow int to be float
                continue
            if not isinstance(data[key], Schema.SCHEMA_DEF[key]):
                print(f'Key "{key}" is not of type {Schema.SCHEMA_DEF[key].__name__}.')
                return False
        return True


def read_robot_status(robot_status):
    # NOTE: the x, y, z, roll, pitch, yaw are represented in terms of robot joints
    # we will need to change this convention soon.
    pos_dict = dict()
    pos_dict['lift_effort'] = robot_status['lift']['force']
    pos_dict['arm_effort'] = robot_status['arm']['force']
    pos_dict['roll_effort'] = robot_status['end_of_arm']['wrist_roll']['effort']
    pos_dict['pitch_effort'] = robot_status['end_of_arm']['wrist_pitch']['effort']
    pos_dict['yaw_effort'] = robot_status['end_of_arm']['wrist_yaw']['effort']
    pos_dict['gripper_effort'] = robot_status['end_of_arm']['stretch_gripper']['effort']

    # if pos_dict['lift_effort'] < -75:
    #     print('Robot not ok, too much lift force')
    #     return False, None

    pos_dict['x'] = robot_status['base']['x']
    pos_dict['theta'] = robot_status['base']['theta']

    pos_dict['z'] = robot_status['lift']['pos']
    pos_dict['y'] = robot_status['arm']['pos']
    pos_dict['roll'] = robot_status['end_of_arm']['wrist_roll']['pos']
    pos_dict['pitch'] = robot_status['end_of_arm']['wrist_pitch']['pos']
    pos_dict['yaw'] = robot_status['end_of_arm']['wrist_yaw']['pos']
    pos_dict['gripper'] = robot_status['end_of_arm']['stretch_gripper']['pos_pct']

    # print(json.dumps(robot_status['base'], indent=4))
    return pos_dict

def do_vertical_control_loop(server, z, sum_force, peak_list):
    if sum_force <= 0:
        server.send_payload({'z': z - 0.002})
    elif sum_force < 100 or len(peak_list) < 2:
        server.send_payload({'z': z - 0.001})
    elif sum_force > 3000:
        server.send_payload({'z': z + 0.001})
