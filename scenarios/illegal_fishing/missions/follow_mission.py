import asyncio
import numpy as np
from missions.mission import MissionBase
from mavsdk.mission import MissionItem, MissionPlan

from missions.generate_trajectory import get_chungdo_obstacles, generate_trajectory

obstacles = get_chungdo_obstacles()

class FollowMission(MissionBase):

    def __init__(self, vehicle, target, vehicle_surveillance, *args, on_arrived=None, **kwargs):
        super().__init__(vehicle, *args, **kwargs)
        self.target = target
        self.vehicle_surveillance = vehicle_surveillance
        self.on_arrived = on_arrived

    async def initialize(self):
        await super().initialize()

    def set_target(self, target):
        self.target = target

    def get_coroutines(self):
        follow_cor = asyncio.ensure_future(self.follow())
        return [follow_cor]

    async def follow(self):
        while True:
            try:
                _, traget_position = self.vehicle_surveillance.get_by_port(self.target._port)
            except ValueError:
                await asyncio.sleep(1)
                continue

            if traget_position is None:
                await asyncio.sleep(1)
                continue
            
            current_position = await self.get_position()

            distance = np.linalg.norm(traget_position - current_position)
            if distance < 0.001:
                print(f"Vehicle {self.vehicle._port} arrived at the target vehicle {self.target._port}")
                if self.on_arrived is not None:
                    self.on_arrived(self.target)

            waypoints = np.concatenate([[current_position], [traget_position]])

            trajectory = generate_trajectory(waypoints, obstacles)

            mission_items = []
            for lon, lat in trajectory:
                mission_items.append(MissionItem(
                    latitude_deg=lat,                               # Latitude in degrees (range: -90 to +90)
                    longitude_deg=lon,                              # Longitude in degrees (range: -180 to +180)
                    relative_altitude_m=0,        # Altitude relative to takeoff altitude in metres
                    speed_m_s=10,                            # Speed to use after this mission item (in metres/second)
                    is_fly_through=True,                            # True will make the drone fly through without stopping, while false will make the drone stop on the waypoint
                    gimbal_pitch_deg=float('nan'),                  # Gimbal pitch (in degrees)
                    gimbal_yaw_deg=float('nan'),                    # Gimbal yaw (in degrees)
                    camera_action=MissionItem.CameraAction.NONE,    # Camera action to trigger at this mission item
                    loiter_time_s=float('nan'),                     # Loiter time (in seconds)
                    camera_photo_interval_s=float('nan'),           # Camera photo interval to use after this mission item (in seconds)
                    acceptance_radius_m=float('nan'),               # Radius for completing a mission item (in metres)
                    yaw_deg=float('nan'),                           # Absolute yaw angle (in degrees)
                    camera_photo_distance_m=float('nan'),           # Camera photo distance to use after this mission item (in meters)
                    vehicle_action=MissionItem.VehicleAction.NONE)) # Vehicle action to trigger at this mission item.

            mission_plan = MissionPlan(mission_items)

            await self.vehicle.mission.upload_mission(mission_plan)

            await self.vehicle.mission.start_mission()

            await asyncio.sleep(1)