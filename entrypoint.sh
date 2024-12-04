#!/usr/bin/env bash

set -e
source /root/px4_ros2_ws/install/setup.bash
source /root/a4_models/install/local_setup.bash

ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock &
exec "$@"
