#!/usr/bin/env bash
WORLD=c-track1

# Start Gazebo
GZ_SIM_RESOURCE_PATH=/root/a4_models/models gz sim -v -r /root/a4_models/worlds/${WORLD}.sdf &
echo "Waiting for Gazebo..." && sleep 10

# Spawn vehicles
# Tutorial: https://docs.px4.io/main/en/sim_gazebo_gz/multi_vehicle_simulation.html#multiple-vehicles-with-ros-2-and-gazebo

# Spawn quadrotors
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=200,320,0,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth /root/PX4-Autopilot/build/px4_sitl_default/bin/px4 -i 1 > /dev/null 2>&1 &
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=202,320,0,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth /root/PX4-Autopilot/build/px4_sitl_default/bin/px4 -i 2 > /dev/null 2>&1 &

# Spawn rover
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=200,322,0,0,0,0 PX4_SYS_AUTOSTART=4009 PX4_SIM_MODEL=gz_r1_rover /root/PX4-Autopilot/build/px4_sitl_default/bin/px4 -i 3 > /dev/null 2>&1 &

# Uncomment this to enable ROS2 communication with the PX4 SITL
# MicroXRCEAgent udp4 -p 8888 &

# Run the script here
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python3 ${SCRIPT_DIR}/mission_single.py
# python3 ${SCRIPT_DIR}/mission_multiple.py

tail -f /dev/null
