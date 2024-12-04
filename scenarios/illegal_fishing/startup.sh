#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

WORLD=harmonic_terrain

# Start Gazebo
GZ_SIM_RESOURCE_PATH=/root/a4_models/models gz sim -r /root/a4_models/worlds/${WORLD}.sdf &
echo "Waiting for Gazebo..." && sleep 10

# Spawn vehicles
# Tutorial: https://docs.px4.io/main/en/sim_gazebo_gz/multi_vehicle_simulation.html#multiple-vehicles-with-ros-2-and-gazebo

# Spawn quadrotors
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=0,10,1.3,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 1 > /dev/null 2>&1 &
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=2,10,1.3,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 2 > /dev/null 2>&1 &

# Spawn rover
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=0,50,0,0,0,1.57 PX4_SYS_AUTOSTART=22000 PX4_SIM_MODEL=wam-v ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 3 > /dev/null 2>&1 &

sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=5,50,0,0,0,1.57 PX4_SYS_AUTOSTART=22000 PX4_SIM_MODEL=wam-v ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 4 > /dev/null 2>&1 &

sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=10,50,0,0,0,1.57 PX4_SYS_AUTOSTART=22000 PX4_SIM_MODEL=wam-v ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 5 > /dev/null 2>&1 &

# Run the script here
# python3 ${SCRIPT_DIR}/mission_single.py

tail -f /dev/null
