# Simulation Scenarios Development

Each scenario has `startup.sh` file that will be called by Docker.

## How to use `startup.sh`

Copy the existing `startup.sh` into another new scenario folder

```bash
#!/usr/bin/env bash
WORLD=c-track1

# Start Gazebo
GZ_SIM_RESOURCE_PATH=${MODELS_PATH}/models gz sim -r ${MODELS_PATH}/worlds/${WORLD}.sdf &
echo "Waiting for Gazebo..." && sleep 10

# Spawn vehicles
# Tutorial: https://docs.px4.io/main/en/sim_gazebo_gz/multi_vehicle_simulation.html#multiple-vehicles-with-ros-2-and-gazebo

# Spawn quadrotors
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=200,320,0,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 1 > /dev/null 2>&1 &
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=202,320,0,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 2 > /dev/null 2>&1 &

# Spawn rover
sleep 5 && echo "Spawning..."
PX4_GZ_MODEL_POSE=200,322,0,0,0,0 PX4_SYS_AUTOSTART=4009 PX4_SIM_MODEL=gz_r1_rover ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 3 > /dev/null 2>&1 &

# Run the script here
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python3 ${SCRIPT_DIR}/mission_single.py
# python3 ${SCRIPT_DIR}/mission_multiple.py

tail -f /dev/null
```

- The first line, `WORLD=c-track1` refers to the world file to load, located at the `a4_models/worlds` folder.
- Next lines launch the Gazebo using the chosen world
- Next, you need to launch the PX4 vehicles.
```bash
PX4_GZ_MODEL_POSE=200,320,0,0,0,0 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_depth ${PX4_PATH}/build/px4_sitl_default/bin/px4 -i 1 > /dev/null 2>&1 &
```
- `PX4_GZ_MODEL_POSE` defines the initial position of the vehicle (`x`, `y`, `z`, `roll`, `pitch`, `yaw`)
- `PX4_SYS_AUTOSTART` defines the PX4 airframe to use for vehicle (refer to table below)
- `PX4_SIM_MODEL` defines the vehicle model to be used from `a4_models/models` folder.
- `-i X` refers to the port used for communication with the vehicle. Vehicle `X` will listen at UDP port `1454X`
- `> /dev/null 2>&1` is for repress the output of PX4 (without doing this, connection tends to be slower).
- The last `&` is to prevent the command blocking the process, so we can spawn multiple vehicles.

To run the script, you can call the script directly after vehicle spawns or by accessing the Docker terminal using `docker exec -it a4-simulation bash`

## Script development

There are two ways to develop the scripts:
1. Using [mavsdk-python](https://mavsdk.mavlink.io/main/en/python/quickstart.html).
    - This is the easiest way to communicate with vehicle.
    - This library utilizes MAVLINK with UDP port of the vehicle (`1454X`)
    - Take a look at `scenarios/c-track` folder for example implementation
    - Or visit [here](https://github.com/mavlink/MAVSDK-Python/tree/main/examples) for more examples.
2. Using `ROS2` with `offboard` flight mode. Examples: [[1]](https://docs.px4.io/main/en/ros2/offboard_control.html) [[2]](https://github.com/Jaeyoung-Lim/px4-offboard)
    - This method is a bit complicated, but allowing flexible communication to the vehicle
    - If you are familiar with ROS 2, you may prefer using this method.


If you need to install additional packages, like `numpy`, modify the `Dockerfile` and add commands like

```dockerfile
RUN pip3 install numpy
```

After that, rebuild the docker image by running command
```bash
docker compose build
```