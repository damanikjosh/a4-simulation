# A4 Simulation

## Overview
A4 Simulator is a Gazebo harmonic + PX4 + ROS2 simulator using Docker. This simulator is designed to provide a comprehensive environment for testing and development.

## Prerequisites
- Ubuntu 20.04 or newer
- [Docker](https://docs.docker.com/engine/install/ubuntu/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/damanikjosh/a4-simulation.git
cd a4-simulation
```

### Step 2: Download Additional Files

Download `a4_models.zip` from [this link](http://a4-simulation.r2.damanikjosh.com/a4_models.zip), and unzip it on project root folder

Or, you can use command
```bash
wget http://a4-simulation.r2.damanikjosh.com/a4_models.zip
unzip a4_models.zip
```

### Step 4: Build the Docker Image

```bash
docker compose build
```

### Step 5: Run the Simulator

On `docker-compose.yml` change the `command` to the `startup.sh` on the scenario folder to run. For example: `/root/scenarios/c-track/startup.sh`.

After that run command
```bash
xhost +local:docker
docker compose up
```

### Step 6: Debugging

To access the terminal inside docker run command
```bash
docker exec -it a4-simulation bash
```

### Step 7: Manual Control

Additionally, you can control the vehicles manually using QGroundControl. You can download it [here](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html)

## Development
- Click [here](docs/scenario_development.md) for guide on building new scenarios.

- Click [here](docs/gazebo_world.md) for guide on modifying Gazebo world.
