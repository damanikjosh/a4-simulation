import asyncio
import numpy as np
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

from task_planner.read_objectives import read_objectives
from task_planner.process_task import process_task
from task_planner.solve_task import solve_task

from missions.waypoints_mission import WaypointsMission
from missions.surveillance_mission import SurveillanceMission
from missions.follow_mission import FollowMission
from surveillance.vehicle_positions_surveillance import VehiclePositionSurveillance

import os

base_path = os.path.dirname(os.path.realpath(__file__))

async def initialize_vehicle(port):
    vehicle = System(port=port)
    vehicle.port = port
    await vehicle.connect(system_address=f"udp://:{port}")

    print("Waiting for vehicle to connect...")
    async for state in vehicle.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to vehicle on {port}!")
            break

    return vehicle

async def get_position(vehicle):
    print("Waiting for vehicle to have a global position estimate...")
    async for health in vehicle.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print(f"-- Global position estimate OK")
            break

    async for position in vehicle.telemetry.position():
        return np.array([position.longitude_deg, position.latitude_deg])

async def upload_mission(vehicle, lonlat_waypoints, altitude=30):
    mission_items = []
    for lon, lat in lonlat_waypoints:
        mission_items.append(MissionItem(
            latitude_deg=lat,                               # Latitude in degrees (range: -90 to +90)
            longitude_deg=lon,                              # Longitude in degrees (range: -180 to +180)
            relative_altitude_m=altitude,                   # Altitude relative to takeoff altitude in metres
            speed_m_s=10,                                   # Speed to use after this mission item (in metres/second)
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

    await vehicle.mission.set_return_to_launch_after_mission(True)

    print("-- Uploading mission")
    await vehicle.mission.upload_mission(mission_plan)

coroutines = []
task_points = []
task_reqs = []
task_done = []
task_types = []

solution_idx = []

async def reset():
    for coroutine in coroutines:
        await coroutine.cancel()
        del coroutine

async def plan_mission(vehicle, task_points, task_reqs, task_done, task_types):
    pass

async def run():

    
    # Define the drone ports and waypoints
    
    drone1 = await initialize_vehicle(14541)
    drone2 = await initialize_vehicle(14542)
    drone3 = await initialize_vehicle(14543)

    usv4 = await initialize_vehicle(14544)
    usv5 = await initialize_vehicle(14545)

    enemy8 = await initialize_vehicle(14548)
    enemy9 = await initialize_vehicle(14549)

    drone1_position = await get_position(drone1)
    drone2_position = await get_position(drone2)
    drone3_position = await get_position(drone3)

    # usv4_position = await get_position(usv4)
    # usv5_position = await get_position(usv5)

    # vehicle_points = [drone1_position, drone2_position, drone3_position]
    # vehicle_points = [usv4_position, usv5_position]

    # obj1_points, obj2_points, obj3_points = read_objectives('data/T_Objectives_latlon.xlsx')
    obj1_points, obj2_points, obj3_points = read_objectives(os.path.join(base_path, 'data/T_Objectives_latlon.xlsx'))
    # points, reqs, done, types = process_task(obj1_points, obj2_points, obj3_points)
    
    obj1_vehicle_points = [drone1_position, drone2_position, drone3_position]
    obj1_reqs = np.zeros((len(obj1_points), len(obj1_points)))
    obj1_done = np.zeros(len(obj1_points))

    obj1_solution_points, obj1_solution_idx = solve_task(obj1_points, obj1_reqs, obj1_done, obj1_vehicle_points)
    
    enemies_surveillancs = VehiclePositionSurveillance([enemy8, enemy9])

    enemy_endopint = [127.079252,  34.376558]
    enemy8_waypoint_mission = WaypointsMission(enemy8, [enemy_endopint], autostart=False)
    enemy9_waypoint_mission = WaypointsMission(enemy9, [enemy_endopint], autostart=False)

    def on_usv4_arrived(target):
        enemy8_waypoint_mission.enable()

    def on_usv5_arrived(target):
        enemy9_waypoint_mission.enable()

    usv4_follow_mission = FollowMission(usv4, enemy8, enemies_surveillancs, autostart=False, on_arrived=on_usv4_arrived)
    usv5_follow_mission = FollowMission(usv5, enemy9, enemies_surveillancs, autostart=False, on_arrived=on_usv5_arrived)

    def on_enemy_found(enemies):
        for enemy in enemies:
            if enemy == enemy8:
                usv4_follow_mission.enable()
            elif enemy == enemy9:
                usv5_follow_mission.enable()


    drone1_surveillance_mission = SurveillanceMission(drone1, obj1_solution_points[0], enemies_surveillancs, on_enemy_found)
    drone2_surveillance_mission = SurveillanceMission(drone2, obj1_solution_points[1], enemies_surveillancs, on_enemy_found)
    drone3_surveillance_mission = SurveillanceMission(drone3, obj1_solution_points[2], enemies_surveillancs, on_enemy_found)

    # usv4_surveillance_mission = SurveillanceMission(usv4, solution_points[3], solution_idx[3], enemies_surveillancs)
    # usv5_surveillance_mission = SurveillanceMission(usv5, solution_points[4], solution_idx[4], enemies_surveillancs)

    await drone1_surveillance_mission.initialize()
    await drone2_surveillance_mission.initialize()
    await drone3_surveillance_mission.initialize()

    await usv4_follow_mission.initialize()
    await usv5_follow_mission.initialize()

    await enemy8_waypoint_mission.initialize(return_to_launch_after_mission=False)
    await enemy9_waypoint_mission.initialize(return_to_launch_after_mission=False)

    coroutines.append(enemies_surveillancs.run())
    coroutines.append(drone1_surveillance_mission.run())
    coroutines.append(drone2_surveillance_mission.run())
    coroutines.append(drone3_surveillance_mission.run())
    coroutines.append(usv4_follow_mission.run())
    coroutines.append(usv5_follow_mission.run())
    coroutines.append(enemy8_waypoint_mission.run())
    coroutines.append(enemy9_waypoint_mission.run())

    # Start missions in parallel
    await asyncio.gather(*coroutines)


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
