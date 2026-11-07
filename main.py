from PySide6.QtWidgets import QApplication

from drone.drone import Drone
from drone.drone_manager import DroneManager
from simulation.simulator import DroneSimulator
from gui.main_window import MainWindow


app = QApplication([])


manager = DroneManager()

drone1 = Drone("D001", "Drone Alpha", 100, 200)
drone2 = Drone("D002", "Drone Beta", 300, 400)
drone3 = Drone("D003", "Drone Gamma", 500, 600)

drone1.status = "FLYING"
drone2.status = "FLYING"
drone3.status = "IDLE"


manager.add_drone(drone1)
manager.add_drone(drone2)
manager.add_drone(drone3)


simulator = DroneSimulator(manager)


window = MainWindow(simulator)


window.show()


app.exec()