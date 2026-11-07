
class Drone:
    def __init__(self, drone_id, name, x=0, y=0):
        self.drone_id = drone_id
        self.name = name

        # Current position
        self.x = x
        self.y = y

        # Home position
        self.home_x = x
        self.home_y = y

        # Battery information
        self.battery = 100
        self.low_battery_threshold = 30
        self.critical_battery_threshold = 15
        self.low_battery_alerted = False

        # Movement information
        self.speed = 0
        self.heading = 0

        # Drone status
        self.status = "IDLE"

        # Failure information
        self.failure_reason = None

    def get_status(self):
        return self.status

    def is_available(self):
        return (
            self.status == "IDLE"
            and self.battery > self.critical_battery_threshold
        )
