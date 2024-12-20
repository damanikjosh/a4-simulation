#!/usr/bin/env bash

export PX4_SIM_HOST_ADDR=127.0.0.1

# echo "Listening on port 4561..."
PX4_SIM_MODEL=none_iris /root/PX4-Autopilot/build/px4_sitl_default/bin/px4 -i 1 -d &
PX4_SIM_MODEL=none_iris /root/PX4-Autopilot/build/px4_sitl_default/bin/px4 -i 2 -d &

tail -f /dev/null