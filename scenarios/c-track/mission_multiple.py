import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

async def initialize_vehicle(port, lon_lat_waypoints, altitude):
    vehicle = System(port=port)
    vehicle.port = port
    await vehicle.connect(system_address=f"udp://:{port}")

    print("Waiting for vehicle to connect...")
    async for state in vehicle.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to vehicle on {port}!")
            break

    mission_items = []
    for lon, lat in lon_lat_waypoints:
        mission_items.append(MissionItem(
            latitude_deg=lat,                               # Latitude in degrees (range: -90 to +90)
            longitude_deg=lon,                              # Longitude in degrees (range: -180 to +180)
            relative_altitude_m=altitude,                   # Altitude relative to takeoff altitude in metres
            speed_m_s=5,                                    # Speed to use after this mission item (in metres/second)
            is_fly_through=True,                            # True will make the drone fly through without stopping, while false will make the drone stop on the waypoint
            gimbal_pitch_deg=float('nan'),                  # Gimbal pitch (in degrees)
            gimbal_yaw_deg=float('nan'),                    # Gimbal yaw (in degrees)
            camera_action=MissionItem.CameraAction.NONE,    # Camera action to trigger at this mission item
            loiter_time_s=float('nan'),                     # Loiter time (in seconds)
            camera_photo_interval_s=float('nan'),           # Camera photo interval to use after this mission item (in seconds)
            acceptance_radius_m=3,                          # Radius for completing a mission item (in metres)
            yaw_deg=float('nan'),                           # Absolute yaw angle (in degrees)
            camera_photo_distance_m=float('nan'),           # Camera photo distance to use after this mission item (in meters)
            vehicle_action=MissionItem.VehicleAction.NONE)) # Vehicle action to trigger at this mission item.
    
    mission_plan = MissionPlan(mission_items)

    await vehicle.mission.set_return_to_launch_after_mission(True)

    print("-- Uploading mission")
    await vehicle.mission.upload_mission(mission_plan)

    return vehicle


async def run():
    # Define the drone ports and waypoints
    
    lon_lat_waypoints_drone1 = [
        (127.442831, 36.728146),
        (127.442825, 36.727921),
        (127.442821, 36.727695),
        (127.443385, 36.727709),
        (127.443378, 36.727942),
        (127.443381, 36.728158),
    ]
    drone1 = await initialize_vehicle(14541, lon_lat_waypoints_drone1, 30)

    lon_lat_waypoints_drone2 = [
        (127.443381, 36.728158),
        (127.443378, 36.727942),
        (127.443385, 36.727709),
        (127.443953, 36.727715),
        (127.443949, 36.727953),
        (127.443951, 36.728175),
    ]
    drone2 = await initialize_vehicle(14542, lon_lat_waypoints_drone2, 35)

    lon_lat_waypoints_rover = [
        (127.443165, 36.728335),
        (127.443161, 36.728181),
        (127.442836, 36.728183),
        # Additional points here
        (127.443161, 36.728181),
        (127.443165, 36.728335),
    ]
    rover = await initialize_vehicle(14543, lon_lat_waypoints_rover, 0)

    vehicles = [drone1, drone2, rover]

    # Start missions in parallel
    tasks = [start_mission(vehicle) for vehicle in vehicles]
    await asyncio.gather(*tasks)




async def start_mission(vehicle):
    """Arm the vehicle and start its mission."""
    print(f"Waiting for vehicle on {vehicle.port} to have a global position estimate...")
    async for health in vehicle.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print(f"-- Global position estimate OK for vehicle on {vehicle.port}")
            break

    print(f"-- Arming vehicle on {vehicle.port}")
    await vehicle.action.arm()

    print(f"-- Starting mission for vehicle on {vehicle.port}")
    await vehicle.mission.start_mission()

    # Monitor mission progress
    print_mission_progress_task = asyncio.ensure_future(print_mission_progress(vehicle, vehicle.port))
    running_tasks = [print_mission_progress_task]

    # Wait for the mission to complete
    await observe_is_in_air(vehicle, running_tasks, vehicle.port)


async def print_mission_progress(vehicle, port):
    async for mission_progress in vehicle.mission.mission_progress():
        print(f"Vehicle on {port} Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")


async def observe_is_in_air(vehicle, running_tasks, port):
    """Monitors whether the vehicle is flying or not and
    returns after landing."""

    was_in_air = False

    async for is_in_air in vehicle.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            print(f"-- Vehicle on {port} has landed.")
            return


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
