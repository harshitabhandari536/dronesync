
import sqlite3
from pathlib import Path
from contextlib import closing


# Database file in the main project folder.
DB_PATH = Path(__file__).resolve().parent.parent / "dronesync.db"


class DatabaseManager:

    def __init__(self):
        self.create_tables()

    def connect(self):
        return sqlite3.connect(DB_PATH)

    # -----------------------------------
    # CREATE DATABASE TABLES
    # -----------------------------------
    def create_tables(self):

        with closing(self.connect()) as conn:
            with conn:

                # Drone table: latest drone information.
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS drones (
                        drone_id TEXT PRIMARY KEY,
                        name TEXT,
                        x REAL,
                        y REAL,
                        speed REAL,
                        battery REAL,
                        status TEXT,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Task table: task information.
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        task_id TEXT PRIMARY KEY,
                        drone_id TEXT,
                        arrival_time INTEGER,
                        burst_time INTEGER,
                        remaining_burst_time INTEGER,
                        priority INTEGER,
                        status TEXT,
                        start_time INTEGER,
                        completion_time INTEGER
                    )
                """)

                # Drone history: recorded drone positions.
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS drone_history (
                        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        simulation_time INTEGER,
                        drone_id TEXT,
                        x REAL,
                        y REAL,
                        speed REAL,
                        battery REAL,
                        status TEXT,
                        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # NEW: Emergency and system alerts.
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        simulation_time INTEGER,
                        drone_id TEXT,
                        alert_type TEXT,
                        message TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)

    # -----------------------------------
    # SAVE LATEST DRONE INFORMATION
    # -----------------------------------
    def save_drone(self, drone):

        with closing(self.connect()) as conn:
            with conn:

                conn.execute("""
                    INSERT INTO drones (
                        drone_id, name, x, y,
                        speed, battery, status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(drone_id) DO UPDATE SET
                        name = excluded.name,
                        x = excluded.x,
                        y = excluded.y,
                        speed = excluded.speed,
                        battery = excluded.battery,
                        status = excluded.status,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    drone.drone_id,
                    drone.name,
                    drone.x,
                    drone.y,
                    drone.speed,
                    drone.battery,
                    drone.status
                ))

    # -----------------------------------
    # SAVE TASK INFORMATION
    # -----------------------------------
    def save_task(self, task):

        with closing(self.connect()) as conn:
            with conn:

                conn.execute("""
                    INSERT INTO tasks (
                        task_id,
                        drone_id,
                        arrival_time,
                        burst_time,
                        remaining_burst_time,
                        priority,
                        status,
                        start_time,
                        completion_time
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(task_id) DO UPDATE SET
                        drone_id = excluded.drone_id,
                        remaining_burst_time =
                            excluded.remaining_burst_time,
                        status = excluded.status,
                        start_time = excluded.start_time,
                        completion_time = excluded.completion_time
                """, (
                    task.task_id,
                    task.drone_id,
                    task.arrival_time,
                    task.original_burst_time,
                    task.remaining_burst_time,
                    task.priority,
                    task.status,
                    task.start_time,
                    task.completion_time
                ))

    # -----------------------------------
    # SAVE DRONE MOVEMENT HISTORY
    # -----------------------------------
    def save_drone_history(self, drone, simulation_time):

        with closing(self.connect()) as conn:
            with conn:

                conn.execute("""
                    INSERT INTO drone_history (
                        simulation_time,
                        drone_id,
                        x,
                        y,
                        speed,
                        battery,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    simulation_time,
                    drone.drone_id,
                    drone.x,
                    drone.y,
                    drone.speed,
                    drone.battery,
                    drone.status
                ))

    # -----------------------------------
    # SAVE EMERGENCY OR SYSTEM ALERT
    # -----------------------------------
    def save_alert(
        self,
        simulation_time,
        drone_id,
        alert_type,
        message
    ):

        with closing(self.connect()) as conn:
            with conn:

                conn.execute("""
                    INSERT INTO alerts (
                        simulation_time,
                        drone_id,
                        alert_type,
                        message
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    simulation_time,
                    drone_id,
                    alert_type,
                    message
                ))

    # -----------------------------------
    # GET ALL ALERTS
    # -----------------------------------
    def get_all_alerts(self):

        with closing(self.connect()) as conn:

            return conn.execute("""
                SELECT *
                FROM alerts
                ORDER BY alert_id DESC
            """).fetchall()

    # -----------------------------------
    # GET NEXT UNUSED TASK NUMBER
    # -----------------------------------
    def get_next_task_number(self):

        rows = self.get_all_tasks()

        highest_number = 0

        for row in rows:
            task_id = row[0]

            if task_id.startswith("T") and task_id[1:].isdigit():
                number = int(task_id[1:])
                highest_number = max(highest_number, number)

        return highest_number + 1

    # -----------------------------------
    # GET ALL DRONES
    # -----------------------------------
    def get_all_drones(self):

        with closing(self.connect()) as conn:
            return conn.execute("""
                SELECT * FROM drones
                ORDER BY drone_id
            """).fetchall()

    # -----------------------------------
    # GET ALL TASKS
    # -----------------------------------
    def get_all_tasks(self):

        with closing(self.connect()) as conn:
            return conn.execute("""
                SELECT * FROM tasks
                ORDER BY arrival_time, task_id
            """).fetchall()

    # -----------------------------------
    # GET DRONE MOVEMENT HISTORY
    # -----------------------------------
    def get_drone_history(self, drone_id=None):

        with closing(self.connect()) as conn:

            if drone_id is None:
                return conn.execute("""
                    SELECT * FROM drone_history
                    ORDER BY history_id
                """).fetchall()

            return conn.execute("""
                SELECT * FROM drone_history
                WHERE drone_id = ?
                ORDER BY history_id
            """, (drone_id,)).fetchall()
