#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

WORLD=chungdo

# Start Gazebo
GZ_SIM_RESOURCE_PATH=/root/a4_models/models gz sim -r /root/a4_models/worlds/${WORLD}.sdf &
echo "Waiting for Gazebo..." && sleep 5

# Spawn vehicles
# Tutorial: https://docs.px4.io/main/en/sim_gazebo_gz/multi_vehicle_simulation.html#multiple-vehicles-with-ros-2-and-gazebo

# Spawn quadrotors
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=-500,-200,2,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth /root/PX4-Autopilot/build/px4_sitl_default/bin/px4 -i 1 > /dev/null 2>&1 &
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=-500,-202,2,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth /root/PX4-Autopilot/build/px4_sitl_default/bin/px4 -i 2 > /dev/null 2>&1 &

# Spawn rover
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=-600,-180,0,0,0,3.14 PX4_SYS_AUTOSTART=22000 PX4_SIM_MODEL=wam-v /root/PX4-Autopilot/build/px4_sitl_default/bin/px4 -i 3 > /dev/null 2>&1 &
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=-900,-180,0,0,0,3.14 PX4_SYS_AUTOSTART=22001 PX4_SIM_MODEL=vessel-e /root/PX4-Autopilot/build/px4_sitl_default/bin/px4 -i 4 > /dev/null 2>&1 &

# Run the script here
# python3 ${SCRIPT_DIR}/mission_single.py

tail -f /dev/null
