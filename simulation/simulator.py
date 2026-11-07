from PySide6.QtCore import QObject, QTimer, Signal

from drone.telemetry import Telemetry
from scheduler.scheduler import Scheduler
from scheduler.task import Task
from database.db_manager import DatabaseManager


class DroneSimulator(QObject):
    alert_raised = Signal(str)

    def __init__(self, drone_manager):
        super().__init__()
        self.drone_manager = drone_manager
        self.scheduler = Scheduler()
        self.database = DatabaseManager()
        self.simulation_time = 0
        self.task_counter = self.database.get_next_task_number()
        self.no_replacement_alerted = set()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_drones)

        for drone in self.drone_manager.get_all_drones():
            self.database.save_drone(drone)

    def start(self, interval=1000):
        self.timer.start(interval)

    def stop(self):
        self.timer.stop()

    def add_manual_task(
        self, drone_id, burst_time, priority, mission_name="Other"
    ):
        drone = self.drone_manager.get_drone(drone_id)
        if drone is None:
            raise ValueError("The selected drone does not exist.")
        if not drone.is_available():
            raise ValueError(
                "This drone is not available. "
                "Choose an idle drone with sufficient battery."
            )
        if burst_time < 1:
            raise ValueError("Burst time must be at least 1.")
        if priority < 1:
            raise ValueError("Priority must be at least 1.")
        if not isinstance(mission_name, str) or not mission_name.strip():
            raise ValueError("Please enter a mission name.")

        task_id = f"T{self.task_counter:03d}"
        self.task_counter += 1
        task = Task(
            task_id=task_id,
            drone_id=drone_id,
            arrival_time=self.simulation_time,
            burst_time=burst_time,
            priority=priority,
            mission_name=mission_name.strip()
        )
        self.scheduler.add_task(task)
        self.database.save_task(task)
        return task

    def raise_alert(self, drone_id, alert_type, message):
        self.database.save_alert(
            self.simulation_time, drone_id, alert_type, message
        )
        self.alert_raised.emit(message)

    def manage_battery(self, drone):
        if drone.status not in ("FLYING", "RETURNING"):
            return
        drone.battery = max(0, drone.battery - 1)

        if (
            drone.battery <= drone.low_battery_threshold
            and not drone.low_battery_alerted
        ):
            drone.low_battery_alerted = True
            self.raise_alert(
                drone.drone_id, "LOW_BATTERY",
                f"WARNING: {drone.drone_id} battery is low ({drone.battery}%)."
            )

        if (
            drone.battery <= drone.critical_battery_threshold
            and drone.status == "FLYING"
        ):
            drone.status = "RETURNING"
            self.raise_alert(
                drone.drone_id, "CRITICAL_BATTERY",
                f"EMERGENCY: {drone.drone_id} battery is critical. Returning home."
            )
            self.reassign_pending_tasks(drone.drone_id, "low battery")

        if drone.battery <= 0:
            drone.status = "FAILED"
            drone.speed = 0
            drone.failure_reason = "Battery depleted"
            self.raise_alert(
                drone.drone_id, "BATTERY_FAILURE",
                f"EMERGENCY: {drone.drone_id} battery depleted. Drone has stopped."
            )
            self.reassign_pending_tasks(drone.drone_id, "battery failure")

    def move_drone(self, drone):
        if drone.status == "FLYING":
            drone.x += 5
            drone.y += 3
            drone.speed = 5
        elif drone.status == "RETURNING":
            dx = drone.home_x - drone.x
            dy = drone.home_y - drone.y
            distance = max(abs(dx), abs(dy))
            if distance <= 5:
                drone.x = drone.home_x
                drone.y = drone.home_y
                drone.speed = 0
                drone.status = "IDLE"
                self.raise_alert(
                    drone.drone_id, "RETURNED_HOME",
                    f"{drone.drone_id} has safely returned home."
                )
            else:
                step = 5 / distance
                drone.x += dx * step
                drone.y += dy * step
                drone.speed = 5

    def find_available_drone(self, excluded_drone_id):
        available_drones = [
            drone for drone in self.drone_manager.get_all_drones()
            if drone.drone_id != excluded_drone_id and drone.is_available()
        ]
        if not available_drones:
            return None
        return max(available_drones, key=lambda drone: drone.battery)

    def reassign_pending_tasks(self, old_drone_id, reason):
        new_drone = self.find_available_drone(old_drone_id)
        if new_drone is None:
            if old_drone_id not in self.no_replacement_alerted:
                self.no_replacement_alerted.add(old_drone_id)
                self.raise_alert(
                    old_drone_id, "NO_AVAILABLE_DRONE",
                    f"WARNING: No available drone to take the pending tasks of {old_drone_id}."
                )
            return

        reassigned_tasks = self.scheduler.reassign_pending_tasks(
            old_drone_id, new_drone.drone_id
        )
        for task in reassigned_tasks:
            self.database.save_task(task)
            self.raise_alert(
                new_drone.drone_id, "TASK_REASSIGNED",
                f"Task {task.task_id} reassigned from {old_drone_id} "
                f"to {new_drone.drone_id} because of {reason}."
            )
        if reassigned_tasks:
            self.no_replacement_alerted.discard(old_drone_id)

    def simulate_drone_failure(self, drone_id):
        drone = self.drone_manager.get_drone(drone_id)
        if drone is None:
            raise ValueError("Drone not found.")
        if drone.status == "FAILED":
            raise ValueError("This drone has already failed.")

        drone.status = "FAILED"
        drone.speed = 0
        drone.failure_reason = "Simulated failure"

        running_task = self.scheduler.running_task
        if running_task is not None and running_task.drone_id == drone_id:
            running_task.status = "READY"
            self.scheduler.ready_queue.insert(0, running_task)
            self.scheduler.running_task = None
            self.scheduler.quantum_used = 0

        self.raise_alert(
            drone_id, "DRONE_FAILURE", f"EMERGENCY: {drone_id} has failed!"
        )
        self.reassign_pending_tasks(drone_id, "drone failure")
        self.database.save_drone(drone)

    def update_drones(self):
        self.simulation_time += 1
        for drone in self.drone_manager.get_all_drones():
            if drone.status in ("FLYING", "RETURNING"):
                self.manage_battery(drone)
                if drone.status in ("FLYING", "RETURNING"):
                    self.move_drone(drone)
            Telemetry(drone).get_data()
            self.database.save_drone(drone)
            self.database.save_drone_history(drone, self.simulation_time)

        if self.scheduler.running_task is None:
            next_task = self.scheduler.start_next_task(self.simulation_time)
            if next_task is not None:
                drone = self.drone_manager.get_drone(next_task.drone_id)
                if drone is not None and drone.status == "IDLE":
                    drone.status = "FLYING"

        completed_task = self.scheduler.execute_current_task(
            self.simulation_time
        )
        if completed_task is not None:
            self.database.save_task(completed_task)
            drone = self.drone_manager.get_drone(completed_task.drone_id)
            if drone is not None and drone.status == "FLYING":
                drone.status = "IDLE"
                drone.speed = 0

        running_task = self.scheduler.running_task
        if running_task is not None:
            self.database.save_task(running_task)
        for task in self.scheduler.get_ready_queue():
            self.database.save_task(task)
