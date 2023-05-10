# stretch_remote

Python library to remotely command and listen to stretch robot.

## Quick Start

```bash
pip install -e .
```

## Usage

Run this on the stretch robot
```bash
python3 stretch_remote/robot_server.py
```

Run this on a remote client via teleop.py
```bash
python3 teleop.py --ip <REMOTE_ROBOT_IP>
```

## Use remote client python lib

```python
from stretch_remote.remote_client import RemoteClient

rc = RemoteClient(ip=<IP>, port=<PORT>)
rc.home()
rc.get_status()
rc.move({'y': 0.1})
```
