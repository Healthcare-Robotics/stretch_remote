# stretch_remote

Python library to remotely control and listen to a stretch robot.

## Quick Start

```bash
pip install -e .
```

## Usage

Run this on the stretch robot
```bash
python3 stretch_remote/robot_server.py
```

Run this on a remote client via `teleop.py`
```bash
python3 teleop.py --ip <REMOTE_ROBOT_IP>
```

## Use remote client python lib

```python
from stretch_remote.remote_client import RemoteClient

rc = RemoteClient(ip=<IP>)

# home the robot
rc.home()

# Get the robot status
s = rc.get_status(compact=True)
print(s)

# Move the robot
# dict is described in absolute joint angles:
rc.move({'y': 0.1})
```

The joint angles dict are represented as:
 - `x y z`: meters
 - `roll pitch yaw`: radians
 - `gripper`: -50 (closed) to 0 (barely closed) to 100 (fully open)

Example: `{'y': 0.1, 'z': 0.75, 'roll': 0, 'pitch': -0.3, 'yaw': 0, 'gripper': 55}`
