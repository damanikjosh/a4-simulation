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

coroutines = []
task_points = []
task_reqs = []
task_done = []
task_types = []

solution_idx = []

async def reset():
    """Cancel and await all running tasks stored in `coroutines`.

    This ensures background gRPC iterators are closed on the main thread
    instead of being implicitly destroyed on worker threads which can
    trigger "cannot join current thread" in aiogrpc.__del__.
    """
    # cancel all tasks
    for task in list(coroutines):
        try:
            task.cancel()
        except Exception:
            pass

    # await their completion
    for task in list(coroutines):
        try:
            await task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"reset: task raised during shutdown: {e}")

    coroutines.clear()

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

    available_drones = [drone1, drone2, drone3]
    available_usvs = [usv4, usv5]

    for drone in available_drones:
        await drone.mission.clear_mission()

    for usv in available_usvs:
        await usv.mission.clear_mission()


    # obj1_points, obj2_points, obj3_points = read_objectives('data/T_Objectives_latlon.xlsx')
    obj1_points, obj2_points, obj3_points = read_objectives(os.path.join(base_path, 'data/T_Objectives_latlon.xlsx'))
    # points, reqs, done, types = process_task(obj1_points, obj2_points, obj3_points)
    
    obj1_vehicle_points = [await get_position(drone) for drone in available_drones]
    obj1_reqs = np.zeros((len(obj1_points), len(obj1_points)))
    obj1_done = np.zeros(len(obj1_points))

    obj1_solution_points, obj1_solution_idx = solve_task(obj1_points, obj1_reqs, obj1_done, obj1_vehicle_points)
    
    enemies_surveillance = VehiclePositionSurveillance([enemy8, enemy9])

    enemy_endpoint = [127.079252,  34.376558]
    enemy8_waypoint_mission = WaypointsMission(enemy8, [enemy_endpoint], autostart=False)
    enemy9_waypoint_mission = WaypointsMission(enemy9, [enemy_endpoint], autostart=False)

    def on_usv4_arrived(vehicle, target):
        enemy8_waypoint_mission.enable()

    def on_usv5_arrived(vehicle, target):
        enemy9_waypoint_mission.enable()

    usv4_follow_mission = FollowMission(usv4, enemy8, enemies_surveillance, autostart=False, on_arrived=on_usv4_arrived)
    usv5_follow_mission = FollowMission(usv5, enemy9, enemies_surveillance, autostart=False, on_arrived=on_usv5_arrived)

    def on_drone1_surveillance_enemy_found(vehicle, enemies):
        drone1_surveillance_mission.disable()
        drone1_follow_mission.set_target(enemies[0])
        drone1_follow_mission.enable()
        on_enemy_found(vehicle, enemies)

    def on_drone2_surveillance_enemy_found(vehicle, enemies):
        drone2_surveillance_mission.disable()
        drone2_follow_mission.set_target(enemies[0])
        drone2_follow_mission.enable()
        on_enemy_found(vehicle, enemies)

    def on_drone3_surveillance_enemy_found(vehicle, enemies):
        drone3_surveillance_mission.disable()
        drone3_follow_mission.set_target(enemies[0])
        drone3_follow_mission.enable()
        on_enemy_found(vehicle, enemies)


    def on_enemy_found(vehicle, enemies):
        for enemy in enemies:
            if enemy == enemy8:
                usv4_follow_mission.enable()
            elif enemy == enemy9:
                usv5_follow_mission.enable()


    drone1_surveillance_mission = SurveillanceMission(drone1, obj1_solution_points[0], enemies_surveillance, on_drone1_surveillance_enemy_found)
    drone2_surveillance_mission = SurveillanceMission(drone2, obj1_solution_points[1], enemies_surveillance, on_drone2_surveillance_enemy_found)
    drone3_surveillance_mission = SurveillanceMission(drone3, obj1_solution_points[2], enemies_surveillance, on_drone3_surveillance_enemy_found)

    drone1_follow_mission = FollowMission(drone1, None, enemies_surveillance, autostart=False, altitude=30)
    drone2_follow_mission = FollowMission(drone2, None, enemies_surveillance, autostart=False, altitude=30)
    drone3_follow_mission = FollowMission(drone3, None, enemies_surveillance, autostart=False, altitude=30)


    await drone1_surveillance_mission.initialize(return_to_launch_after_mission=True)
    await drone2_surveillance_mission.initialize(return_to_launch_after_mission=True)
    await drone3_surveillance_mission.initialize(return_to_launch_after_mission=True)

    await usv4_follow_mission.initialize()
    await usv5_follow_mission.initialize()

    await enemy8_waypoint_mission.initialize()
    await enemy9_waypoint_mission.initialize()

    await drone1_follow_mission.initialize()
    await drone2_follow_mission.initialize()
    await drone3_follow_mission.initialize()

    # Create actual asyncio Tasks so we can cancel/await them later
    coroutines.append(asyncio.create_task(enemies_surveillance.run()))
    coroutines.append(asyncio.create_task(drone1_surveillance_mission.run()))
    coroutines.append(asyncio.create_task(drone2_surveillance_mission.run()))
    coroutines.append(asyncio.create_task(drone3_surveillance_mission.run()))
    coroutines.append(asyncio.create_task(usv4_follow_mission.run()))
    coroutines.append(asyncio.create_task(usv5_follow_mission.run()))
    coroutines.append(asyncio.create_task(enemy8_waypoint_mission.run()))
    coroutines.append(asyncio.create_task(enemy9_waypoint_mission.run()))
    coroutines.append(asyncio.create_task(drone1_follow_mission.run()))
    coroutines.append(asyncio.create_task(drone2_follow_mission.run()))
    coroutines.append(asyncio.create_task(drone3_follow_mission.run()))

    # Start missions in parallel and wait for them. If the main program
    # needs to shut down, call `await reset()` to cancel and join tasks
    try:
        await asyncio.gather(*coroutines)
    finally:
        await reset()


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
