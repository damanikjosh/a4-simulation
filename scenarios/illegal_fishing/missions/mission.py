import asyncio
import numpy as np

class MissionBase:
    def __init__(self, vehicle, *args, autostart=True, **kwargs):
        self.vehicle = vehicle
        self.is_enabled = autostart

        self.is_initialized = False
        self.is_run = False

    # ===============================
    # To be implemented by subclasses
    # ===============================
    async def initialize(self, *args, **kwargs):
        self.is_initialized = True

    async def on_start(self, *args, **kwargs):
        pass

    def get_coroutines(self):
        return []

    # ===============================

    def enable(self):
        self.is_enabled = True
        print(f"Mission enabled for vehicle {self.vehicle._port}")

    async def run(self, *args, **kwargs):
        self.is_run = True

        if not self.is_initialized:
            raise ValueError("Initialize the mission first. Call initialize() method.")

        while not self.is_enabled:
            await asyncio.sleep(1)

        print(f"Waiting for vehicle {self.vehicle._port} to have a global position estimate...")
        async for health in self.vehicle.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print(f"-- Global position estimate OK for vehicle {self.vehicle._port}")
                break
        
        print(f"-- Arming vehicle on {self.vehicle._port}")
        await self.vehicle.action.arm()
        
        print(f"-- Starting mission for vehicle on vehicle {self.vehicle._port}")
        await self.on_start(*args, **kwargs)
        
        # Monitor mission progress
        running_tasks = self.get_coroutines()

        # Wait for the mission to complete
        await self.observe_is_in_air(running_tasks)



    async def observe_is_in_air(self, running_tasks):
        """Monitors whether the vehicle is flying or not and
        returns after landing."""

        was_in_air = False

        async for is_in_air in self.vehicle.telemetry.in_air():
            if is_in_air:
                was_in_air = is_in_air

            if was_in_air and not is_in_air:
                for task in running_tasks:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                print(f"-- Vehicle {self.vehicle._port} on has landed.")
                return
            
    async def get_home_position(self):
        async for home_position in self.vehicle.telemetry.home():
            return np.array([home_position.longitude_deg, home_position.latitude_deg])
            
    async def get_position(self):
        async for position in self.vehicle.telemetry.position():
            return np.array([position.longitude_deg, position.latitude_deg])
