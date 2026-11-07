# Multi-Drone Simulation System

## About the Project

This project is a simple drone simulation system made using Python. It allows users to manage multiple drones, assign tasks to them, and monitor their activities through a desktop application.

The main idea behind this project is to understand how multiple drones can be managed using task scheduling. It also shows how drones can be monitored and how situations like low battery and drone failure can be handled.

## Features

### Drone Dashboard
- View all the drones in one place.
- Check the battery level and current status of each drone.
- Monitor drone speed and position.
- See which task is assigned to a drone.

### Mission Management
Users can assign different missions to drones, such as:

- Surveillance
- Traffic Monitoring
- Parking Monitoring
- Campus Inspection
- School Inspection
- Hostel Area Inspection
- Society Monitoring
- Market Monitoring
- Environmental Monitoring
- Emergency Assessment

Users can also create their own mission by selecting the custom task option.

### Task Scheduling

The project uses three scheduling algorithms to manage tasks:

- **FCFS:** Tasks are handled in the order they arrive.
- **Priority Scheduling:** Tasks with higher priority are selected first.
- **Round Robin:** Each task gets a fixed amount of execution time.

### Battery Management
- Battery decreases while a drone is flying or returning home.
- A warning is shown when the battery becomes low.
- When the battery reaches a critical level, the drone starts returning home.
- A drone is marked as failed if its battery runs out.

### Drone Failure Handling
- Users can simulate a drone failure.
- The system generates an alert when a drone fails.
- Pending tasks can be reassigned to another available drone.

### Database
The project uses SQLite to store drone details, task information, alerts, and drone history.

## Technologies Used

- Python
- PySide6
- SQLite
- Object-Oriented Programming
- CPU Scheduling Algorithms

## Project Structure

```text
dronesync/
│
├── drone/
│   ├── drone.py
│   ├── drone_manager.py
│   └── telemetry.py
│
├── scheduler/
│   ├── scheduler.py
│   └── task.py
│
├── simulation/
│   └── simulator.py
│
├── database/
│   └── db_manager.py
│
├── gui/
│   └── main_window.py
│
├── main.py
├── requirements.txt
└── README.md
```

## How to Run the Project

### Step 1: Clone the repository

```bash
git clone https:https://github.com/harshitabhandari536/dronesync
```

### Step 2: Open the project folder

```bash
cd YOUR-REPOSITORY-NAME
```

### Step 3: Create a virtual environment

```bash
python -m venv venv
```

### Step 4: Activate the environment

For Windows:

```bash
venv\Scripts\activate
```

### Step 5: Install the required library

```bash
pip install -r requirements.txt
```

### Step 6: Run the application

```bash
python main.py
```

## What I Learned

While working on this project, I learned how to:

- Work with Python classes and objects.
- Build a desktop application using PySide6.
- Use scheduling algorithms to manage tasks.
- Store and retrieve data using SQLite.
- Manage drone status and battery levels.
- Handle basic failure situations.
- Connect different parts of a project into one application.

## Future Improvements

Some things I would like to add in the future are:

- Better drone movement and route planning.
- More control over individual drones.
- Improved task scheduling.
- Better ways to handle drone failures.
- More detailed reports and performance information.

## Author

**HARSHITA BHANDARI**

GitHub: https://github.com/harshitabhandari536/dronesync 
