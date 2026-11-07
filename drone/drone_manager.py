from drone.drone import Drone


class DroneManager:
    def __init__(self):
        self.drones = {}

    def add_drone(self, drone):
        self.drones[drone.drone_id] = drone

    def get_drone(self, drone_id):
        return self.drones.get(drone_id)

    def get_all_drones(self):
        return list(self.drones.values())

    def remove_drone(self, drone_id):
        if drone_id in self.drones:
            del self.drones[drone_id]