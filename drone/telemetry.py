class Telemetry:
    def __init__(self, drone):
        self.drone = drone

    def get_data(self):
        return {
            "drone_id": self.drone.drone_id,
            "x": self.drone.x,
            "y": self.drone.y,
            "speed": self.drone.speed,
            "heading": self.drone.heading,
            "battery": self.drone.battery,
            "status": self.drone.status
        }