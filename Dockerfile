FROM damanikjosh/a4-simulation:base
LABEL authors="Joshua J. Damanik <joshuajdmk@gmail.com>"
LABEL version="0.0.1"

COPY a4_models /root/a4_models

WORKDIR /root/a4_models
RUN . /root/px4_ros2_ws/install/setup.sh \
  && colcon build --symlink-install

# Install dependencies here
# For example:
RUN pip3 install --break-system-packages pandas openpyxl pyvrp scikit-learn mip geopandas quart

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
