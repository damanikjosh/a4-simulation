#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# WORLD=nathan
WORLD=nathan
GZ_SIM_RESOURCE_PATH=/root/a4_models/models gz sim -v -r /root/a4_models/worlds/${WORLD}.sdf &
echo "Waiting for Gazebo..." && sleep 5

sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=0,0,0,0,0,0 PX4_SYS_AUTOSTART=22000 PX4_SIM_MODEL=wam-v /root/PX4-Autopilot/build/px4_sitl_default/bin/px4 -i 1 > /dev/null 2>&1 &
# PX4_GZ_MODEL_POSE=10,0,0,0,0,0 PX4_SYS_AUTOSTART=4009 PX4_SIM_MODEL=gz_r1_rover ./build/px4_sitl_default/bin/px4 -i 2 > /dev/null 2>&1 &


tail -f /dev/null