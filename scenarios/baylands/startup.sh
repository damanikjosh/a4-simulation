#!/usr/bin/env bash
WORLD=baylands

# Start Gazebo
GZ_SIM_RESOURCE_PATH=${MODELS_PATH}/models gz sim -v -r ${MODELS_PATH}/worlds/${WORLD}.sdf &
echo "Waiting for Gazebo..." && sleep 5

# Spawn vehicles
# Tutorial: https://docs.px4.io/main/en/sim_gazebo_gz/multi_vehicle_simulation.html#multiple-vehicles-with-ros-2-and-gazebo

# Spawn quadrotors
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=-10,0,0,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 1 > /dev/null 2>&1 &
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=-10,2,0,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 2 > /dev/null 2>&1 &

tail -f /dev/null
