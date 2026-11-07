from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPen, QBrush
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QGroupBox, QComboBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QListWidget, QStackedWidget, QScrollArea, QSizePolicy, QLineEdit
)


# ---------------------------------------------------------
# DRONE MAP
# ---------------------------------------------------------

class DroneView(QWidget):
    def __init__(self, drone):
        super().__init__()
        self.drone = drone
        self.current_task_id = None
        self.setMinimumHeight(300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)

        width, height = self.width(), self.height()
        margin = 42
        plot_width = max(1, width - 2 * margin)
        plot_height = max(1, height - 2 * margin)

        # Grid and axes
        painter.setPen(QPen(Qt.lightGray, 1))
        for i in range(6):
            x = margin + i * plot_width / 5
            y = margin + i * plot_height / 5
            painter.drawLine(int(x), margin, int(x), height - margin)
            painter.drawLine(margin, int(y), width - margin, int(y))

        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(margin, height - margin, width - margin, height - margin)
        painter.drawLine(margin, height - margin, margin, margin)
        painter.drawText(width - margin + 10, height - margin + 5, "X")
        painter.drawText(margin - 20, margin - 10, "Y")
        painter.drawText(margin - 8, height - margin + 20, "0")
        painter.drawText(width - margin - 30, height - margin + 20, "700")

        max_coord = 700
        x = margin + float(self.drone.x) / max_coord * plot_width
        y = height - margin - float(self.drone.y) / max_coord * plot_height
        x = max(margin, min(width - margin, x))
        y = max(margin, min(height - margin, y))

        if self.drone.status == "FAILED":
            color = Qt.red
        elif self.drone.status == "RETURNING":
            color = Qt.darkYellow
        elif self.drone.status == "FLYING":
            color = Qt.blue
        else:
            color = Qt.darkGreen

        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(int(x - 9), int(y - 9), 18, 18)
        painter.setPen(QPen(Qt.black))
        painter.drawText(int(x + 14), int(y - 8), self.drone.drone_id)

        if self.current_task_id:
            painter.setPen(QPen(Qt.black))
            painter.drawText(int(x + 14), int(y + 16),
                             f"Task: {self.current_task_id}")
        painter.end()


# ---------------------------------------------------------
# DRONE CARD
# ---------------------------------------------------------

class DronePanel(QFrame):
    def __init__(self, drone):
        super().__init__()
        self.drone = drone
        self.setObjectName("droneCard")
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)

        title = QLabel(f"{drone.drone_id}  |  {drone.name}")
        title.setObjectName("cardTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.view = DroneView(drone)
        layout.addWidget(self.view, 1)

        telemetry = QGridLayout()
        telemetry.setHorizontalSpacing(24)
        telemetry.setVerticalSpacing(8)

        self.position = QLabel()
        self.speed = QLabel()
        self.heading = QLabel()
        self.battery = QLabel()
        self.status = QLabel()
        self.task = QLabel()

        fields = [
            ("POSITION", self.position),
            ("SPEED", self.speed),
            ("HEADING", self.heading),
            ("BATTERY", self.battery),
            ("STATUS", self.status),
            ("CURRENT TASK", self.task),
        ]
        for index, (name, value) in enumerate(fields):
            cell = QVBoxLayout()
            caption = QLabel(name)
            caption.setObjectName("metricCaption")
            value.setObjectName("metricValue")
            cell.addWidget(caption)
            cell.addWidget(value)
            telemetry.addLayout(cell, index // 3, index % 3)

        layout.addLayout(telemetry)
        self.update_panel(None)

    def update_panel(self, running_task):
        d = self.drone
        self.position.setText(f"X: {d.x:.1f}   Y: {d.y:.1f}")
        self.speed.setText(str(d.speed))
        self.heading.setText(str(d.heading))
        self.battery.setText(f"{d.battery}%")
        self.status.setText(d.status)

        if running_task is not None and running_task.drone_id == d.drone_id:
            self.view.current_task_id = running_task.task_id
            self.task.setText(f"{running_task.task_id} (RUNNING)")
        else:
            self.view.current_task_id = None
            self.task.setText("NONE")

        if d.status == "FAILED" or d.battery <= 15:
            self.battery.setStyleSheet("color: #ff6262; font-weight: 700;")
        elif d.battery <= 30:
            self.battery.setStyleSheet("color: #e6a23c; font-weight: 700;")
        else:
            self.battery.setStyleSheet("color: #42b883; font-weight: 700;")

        status_colors = {
            "FAILED": "#ff6262",
            "RETURNING": "#e6a23c",
            "FLYING": "#5aa9ff",
            "IDLE": "#42b883",
        }
        self.status.setStyleSheet(
            f"color: {status_colors.get(d.status, '#e8edf5')}; font-weight: 700;"
        )
        self.view.update()


# ---------------------------------------------------------
# SCHEDULER INFORMATION
# ---------------------------------------------------------

class SchedulerPanel(QFrame):
    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self.setObjectName("contentCard")
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("CPU SCHEDULER")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.time_label = QLabel("Simulation Time: 0")
        self.algorithm_label = QLabel("Current Algorithm: FCFS")
        self.system_label = QLabel("System Status: STOPPED")
        for label in (self.time_label, self.algorithm_label, self.system_label):
            label.setObjectName("infoLine")
            layout.addWidget(label)

        controls = QGridLayout()
        controls.addWidget(QLabel("Scheduling algorithm"), 0, 0)
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["FCFS", "Priority", "Round Robin"])
        controls.addWidget(self.algorithm_combo, 0, 1)

        controls.addWidget(QLabel("Round Robin time quantum"), 1, 0)
        self.quantum = QSpinBox()
        self.quantum.setRange(1, 20)
        self.quantum.setValue(2)
        controls.addWidget(self.quantum, 1, 1)

        apply_button = QPushButton("APPLY SCHEDULING")
        apply_button.clicked.connect(self.apply_scheduling)
        controls.addWidget(apply_button, 0, 2, 2, 1)
        layout.addLayout(controls)

        running_box = QGroupBox("CURRENT TASK")
        running_grid = QGridLayout(running_box)
        self.running_values = [QLabel("NONE"), QLabel("-"), QLabel("-"), QLabel("-")]
        for row, (name, value) in enumerate(zip(
            ["Task", "Assigned drone", "Priority", "Remaining burst"],
            self.running_values
        )):
            running_grid.addWidget(QLabel(name), row, 0)
            running_grid.addWidget(value, row, 1)
        layout.addWidget(running_box)

        queue_box = QGroupBox("READY QUEUE")
        queue_layout = QVBoxLayout(queue_box)
        self.queue_label = QLabel("EMPTY")
        self.queue_label.setWordWrap(True)
        queue_layout.addWidget(self.queue_label)
        layout.addWidget(queue_box)

        self.completed_label = QLabel("Completed Tasks: 0")
        layout.addWidget(self.completed_label)

        buttons = QHBoxLayout()
        start = QPushButton("START SIMULATION")
        start.setObjectName("primaryButton")
        stop = QPushButton("STOP SIMULATION")
        start.clicked.connect(self.start_simulation)
        stop.clicked.connect(self.stop_simulation)
        buttons.addWidget(start)
        buttons.addWidget(stop)
        layout.addLayout(buttons)

    def start_simulation(self):
        self.simulator.start(1000)
        self.system_label.setText("System Status: RUNNING")

    def stop_simulation(self):
        self.simulator.stop()
        self.system_label.setText("System Status: STOPPED")

    def apply_scheduling(self):
        scheduler = self.simulator.scheduler
        scheduler.set_algorithm(self.algorithm_combo.currentText())
        scheduler.set_time_quantum(self.quantum.value())
        self.algorithm_label.setText(f"Current Algorithm: {scheduler.algorithm}")

    def update_panel(self):
        scheduler = self.simulator.scheduler
        self.time_label.setText(f"Simulation Time: {self.simulator.simulation_time}")
        self.algorithm_label.setText(f"Current Algorithm: {scheduler.algorithm}")

        task = scheduler.running_task
        values = (
            [task.task_id, task.drone_id, str(task.priority),
             str(task.remaining_burst_time)]
            if task is not None else ["NONE", "-", "-", "-"]
        )
        for label, value in zip(self.running_values, values):
            label.setText(value)

        queue = scheduler.get_ready_queue()
        self.queue_label.setText(
            "  →  ".join(task.task_id for task in queue) if queue else "EMPTY"
        )
        self.completed_label.setText(
            f"Completed Tasks: {len(scheduler.completed_tasks)}"
        )


# ---------------------------------------------------------
# MAIN WINDOW WITH TWO CONNECTED PAGES
# ---------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self.drone_panels = []

        self.setWindowTitle("Multi-Drone Simulation System")
        self.resize(1450, 950)
        self.setMinimumSize(1000, 700)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: #111827;
                color: #e8edf5;
                font-size: 13px;
            }
            QLabel#appTitle {
                color: #f8fafc;
                font-size: 23px;
                font-weight: 800;
                padding: 8px;
            }
            QLabel#pageSubtitle {
                color: #9caec5;
                font-size: 13px;
                padding-bottom: 8px;
            }
            QPushButton {
                background: #263449;
                color: #f8fafc;
                border: 1px solid #3d506b;
                border-radius: 7px;
                padding: 10px 16px;
                font-weight: 600;
            }
            QPushButton:hover { background: #344761; }
            QPushButton#navButton {
                background: #1d293b;
                padding: 12px 22px;
                font-size: 14px;
            }
            QPushButton#primaryButton, QPushButton#navActive {
                background: #2563eb;
                border: 1px solid #3b82f6;
            }
            QFrame#droneCard, QFrame#contentCard {
                background: #1b2738;
                border: 1px solid #35465e;
                border-radius: 12px;
            }
            QLabel#cardTitle {
                font-size: 18px;
                font-weight: 700;
                color: #f8fafc;
                padding: 5px;
            }
            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
                color: #f8fafc;
                padding-bottom: 4px;
            }
            QLabel#metricCaption {
                color: #91a4bd;
                font-size: 10px;
                font-weight: 700;
            }
            QLabel#metricValue {
                color: #f8fafc;
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#infoLine {
                color: #dce6f3;
                padding: 3px;
            }
            QGroupBox {
                border: 1px solid #3b4b62;
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px;
                font-weight: 700;
                color: #cbd8e8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QComboBox, QSpinBox {
                background: #263449;
                color: #f8fafc;
                border: 1px solid #465a75;
                border-radius: 6px;
                padding: 8px;
                min-height: 22px;
            }
            QTableWidget, QListWidget {
                background: #172233;
                alternate-background-color: #1e2d42;
                color: #e8edf5;
                border: 1px solid #35465e;
                border-radius: 7px;
                gridline-color: #34445a;
            }
            QHeaderView::section {
                background: #263449;
                color: #e8edf5;
                padding: 9px;
                border: none;
                font-weight: 700;
            }
            QScrollArea { border: none; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("MULTI-DRONE SIMULATION SYSTEM")
        title.setObjectName("appTitle")
        header.addWidget(title)
        header.addStretch()

        self.dashboard_button = QPushButton("DRONE DASHBOARD")
        self.dashboard_button.setObjectName("navButton")
        self.control_button = QPushButton("CONTROL CENTRE")
        self.control_button.setObjectName("navButton")
        self.dashboard_button.clicked.connect(lambda: self.show_page(0))
        self.control_button.clicked.connect(lambda: self.show_page(1))
        header.addWidget(self.dashboard_button)
        header.addWidget(self.control_button)
        root.addLayout(header)

        self.pages = QStackedWidget()
        root.addWidget(self.pages, 1)

        self.dashboard_page = self.build_dashboard_page()
        self.control_page = self.build_control_page()
        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.control_page)
        self.show_page(0)

        self.simulator.alert_raised.connect(self.show_alert)

        self.gui_timer = QTimer(self)
        self.gui_timer.timeout.connect(self.update_gui)
        self.gui_timer.start(150)

    def make_scroll_page(self, content_widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content_widget)
        return scroll

    def build_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        heading = QLabel("LIVE DRONE DASHBOARD")
        heading.setObjectName("sectionTitle")
        subtitle = QLabel(
            "Live positions and telemetry for every drone. "
            "Use Control Centre to schedule tasks and manage emergencies."
        )
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(heading)
        layout.addWidget(subtitle)

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(14)

        drones = self.simulator.drone_manager.get_all_drones()
        for index, drone in enumerate(drones):
            panel = DronePanel(drone)
            grid.addWidget(panel, index // 2, index % 2)
            self.drone_panels.append(panel)

        if not drones:
            empty = QLabel("No drones are registered in the simulation.")
            layout.addWidget(empty)

        layout.addWidget(grid_widget)
        layout.addStretch()
        return self.make_scroll_page(page)

    def build_control_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        heading = QLabel("SIMULATION CONTROL CENTRE")
        heading.setObjectName("sectionTitle")
        subtitle = QLabel(
            "Manage scheduling, create tasks, inspect task progress, "
            "and respond to drone emergencies."
        )
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(heading)
        layout.addWidget(subtitle)

        self.scheduler_panel = SchedulerPanel(self.simulator)
        layout.addWidget(self.scheduler_panel)

        # Manual task creation
        task_box = QGroupBox("CREATE TASK")
        task_layout = QGridLayout(task_box)
        task_layout.addWidget(QLabel("Assign drone"), 0, 0)
        self.drone_combo = QComboBox()
        self.failure_combo = QComboBox()
        drones = self.simulator.drone_manager.get_all_drones()
        for drone in drones:
            label = f"{drone.drone_id} - {drone.name}"
            self.drone_combo.addItem(label, drone.drone_id)
            self.failure_combo.addItem(label, drone.drone_id)
        task_layout.addWidget(self.drone_combo, 0, 1)

        # Mission Library
        task_layout.addWidget(QLabel("Select mission"), 1, 0)
        self.mission_combo = QComboBox()
        self.mission_combo.addItems([
            "Surveillance",
            "Traffic Monitoring",
            "Parking Monitoring",
            "Campus Inspection",
            "School Inspection",
            "Hostel Area Inspection",
            "Society Monitoring",
            "Market Monitoring",
            "Environmental Monitoring",
            "Emergency Assessment",
            "Other / Custom Task"
        ])
        self.mission_combo.currentTextChanged.connect(
            self.update_custom_mission_field
        )
        task_layout.addWidget(self.mission_combo, 1, 1)

        self.custom_mission_label = QLabel("Custom task name")
        self.custom_mission_input = QLineEdit()
        self.custom_mission_input.setPlaceholderText(
            "Enter your custom task"
        )
        task_layout.addWidget(self.custom_mission_label, 1, 2)
        task_layout.addWidget(self.custom_mission_input, 1, 3, 1, 2)
        self.update_custom_mission_field(self.mission_combo.currentText())

        task_layout.addWidget(QLabel("Burst time"), 0, 2)
        self.burst_spin = QSpinBox()
        self.burst_spin.setRange(1, 100)
        self.burst_spin.setValue(5)
        task_layout.addWidget(self.burst_spin, 0, 3)

        task_layout.addWidget(QLabel("Priority (1 = highest)"), 0, 4)
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 10)
        self.priority_spin.setValue(1)
        task_layout.addWidget(self.priority_spin, 0, 5)

        add_button = QPushButton("ADD TASK")
        add_button.setObjectName("primaryButton")
        add_button.clicked.connect(self.add_manual_task)
        task_layout.addWidget(add_button, 0, 6)
        layout.addWidget(task_box)

        # Emergency controls
        failure_box = QGroupBox("EMERGENCY AND FAILURE CONTROL")
        failure_layout = QHBoxLayout(failure_box)
        failure_layout.addWidget(QLabel("Select drone"))
        failure_layout.addWidget(self.failure_combo, 1)
        failure_button = QPushButton("SIMULATE DRONE FAILURE")
        failure_button.clicked.connect(self.simulate_failure)
        failure_layout.addWidget(failure_button, 1)
        layout.addWidget(failure_box)

        # Alerts
        alert_box = QGroupBox("EMERGENCY ALERTS")
        alert_layout = QVBoxLayout(alert_box)
        self.alert_list = QListWidget()
        self.alert_list.setMaximumHeight(150)
        alert_layout.addWidget(self.alert_list)
        layout.addWidget(alert_box)

        # Task table
        table_box = QGroupBox("TASK MANAGEMENT")
        table_layout = QVBoxLayout(table_box)
        self.task_table = QTableWidget(0, 8)
        self.task_table.setHorizontalHeaderLabels([
            "Task ID", "Mission", "Drone", "Arrival",
            "Burst", "Priority", "Remaining", "Status"
        ])
        self.task_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.task_table.verticalHeader().setVisible(False)
        self.task_table.setMinimumHeight(220)
        table_layout.addWidget(self.task_table)
        layout.addWidget(table_box)

        layout.addStretch()
        return self.make_scroll_page(page)

    def show_page(self, index):
        self.pages.setCurrentIndex(index)
        self.dashboard_button.setObjectName(
            "navActive" if index == 0 else "navButton"
        )
        self.control_button.setObjectName(
            "navActive" if index == 1 else "navButton"
        )
        self.dashboard_button.style().unpolish(self.dashboard_button)
        self.dashboard_button.style().polish(self.dashboard_button)
        self.control_button.style().unpolish(self.control_button)
        self.control_button.style().polish(self.control_button)

    def update_custom_mission_field(self, mission):
        is_custom = mission == "Other / Custom Task"
        self.custom_mission_label.setVisible(is_custom)
        self.custom_mission_input.setVisible(is_custom)

    def add_manual_task(self):
        if self.drone_combo.count() == 0:
            QMessageBox.warning(self, "No drones", "No drones are available.")
            return

        selected_mission = self.mission_combo.currentText()
        if selected_mission == "Other / Custom Task":
            mission_name = self.custom_mission_input.text().strip()
            if not mission_name:
                QMessageBox.warning(
                    self, "Missing task name",
                    "Please enter your custom task name."
                )
                return
        else:
            mission_name = selected_mission

        drone_id = self.drone_combo.currentData()
        try:
            task = self.simulator.add_manual_task(
                drone_id, self.burst_spin.value(),
                self.priority_spin.value(), mission_name
            )
        except (ValueError, AttributeError) as error:
            QMessageBox.warning(self, "Could not add task", str(error))
            return

        self.update_task_table()
        QMessageBox.information(
            self, "Task added",
            f"{task.task_id} - {task.mission_name} was added to the ready queue."
        )
        self.custom_mission_input.clear()

    def simulate_failure(self):
        if self.failure_combo.count() == 0:
            return

        drone_id = self.failure_combo.currentData()
        answer = QMessageBox.question(
            self,
            "Confirm drone failure",
            f"Are you sure you want to simulate failure of {drone_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return

        try:
            self.simulator.simulate_drone_failure(drone_id)
        except ValueError as error:
            QMessageBox.warning(self, "Failure simulation", str(error))
            return

        self.update_gui()

    def show_alert(self, message):
        self.alert_list.insertItem(0, message)
        while self.alert_list.count() > 100:
            self.alert_list.takeItem(self.alert_list.count() - 1)

    def update_task_table(self):
        scheduler = self.simulator.scheduler
        tasks = list(scheduler.ready_queue) + list(scheduler.completed_tasks)
        if scheduler.running_task is not None:
            tasks.append(scheduler.running_task)

        tasks.sort(key=lambda task: (task.arrival_time, task.task_id))
        self.task_table.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            values = [
                task.task_id, task.mission_name, task.drone_id,
                str(task.arrival_time), str(task.original_burst_time),
                str(task.priority), str(task.remaining_burst_time), task.status
            ]
            for col, value in enumerate(values):
                self.task_table.setItem(row, col, QTableWidgetItem(value))

    def update_gui(self):
        running_task = self.simulator.scheduler.running_task
        for panel in self.drone_panels:
            panel.update_panel(running_task)

        self.scheduler_panel.update_panel()
        self.update_task_table()

    def closeEvent(self, event):
        # Stop the simulation timer cleanly when the window closes.
        self.simulator.stop()
        event.accept()
