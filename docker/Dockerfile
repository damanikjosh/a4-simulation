FROM osrf/ros:jazzy-simulation
LABEL authors="Joshua J. Damanik <joshuajdmk@gmail.com>"
LABEL version="0.0.1"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
  build-essential \
  python3-pip \
  cmake \
  wget \
  curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /root

RUN git clone https://github.com/PX4/PX4-Autopilot.git

WORKDIR /root/PX4-Autopilot

RUN git submodule update --init --recursive src/modules/mavlink/mavlink \
  && git submodule update --init --recursive src/drivers/cyphal/public_regulated_data_types \
  && git submodule update --init --recursive src/lib/crypto/monocypher \
  && git submodule update --init --recursive src/lib/events/libevents \
  && git submodule update --init --recursive src/lib/crypto/libtomcrypt \
  && git submodule update --init --recursive src/lib/crypto/libtommath \
  && git submodule update --init --recursive src/modules/uxrce_dds_client/Micro-XRCE-DDS-Client \
  && git submodule update --init --recursive src/lib/cdrstream/rosidl \
  && git submodule update --init --recursive Tools/simulation/gz

RUN bash ./Tools/setup/ubuntu.sh --no-nuttx \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git \
  && cd Micro-XRCE-DDS-Agent \
  && mkdir build \
  && cd build \
  && cmake .. \
  && make \
  && make install \
  && cd ../.. \
  && rm -rf Micro-XRCE-DDS-Agent

WORKDIR /root/px4_ros2_ws
RUN git clone https://github.com/PX4/px4_msgs.git src/px4_msgs \
  && git clone https://github.com/PX4/px4_ros_com.git src/px4_ros_com

RUN . /opt/ros/jazzy/setup.sh \
  && colcon build --symlink-install

RUN pip3 install --break-system-packages mavsdk quart

WORKDIR /root/PX4-Autopilot

RUN echo "param set UXRCE_DDS_SYNCT 0" >> ROMFS/px4fmu_common/init.d/rc.vehicle_setup
COPY airframes/ ROMFS/px4fmu_common/init.d-posix/airframes/
RUN make px4_sitl

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]