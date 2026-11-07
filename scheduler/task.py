class Task:
    def __init__(
        self,
        task_id,
        drone_id,
        arrival_time,
        burst_time,
        priority,
        mission_name="Other"
    ):
        self.task_id = task_id
        self.drone_id = drone_id
        self.mission_name = mission_name

        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.original_burst_time = burst_time
        self.remaining_burst_time = burst_time
        self.priority = priority

        self.status = "READY"

        self.start_time = None
        self.completion_time = None
        self.waiting_time = None
        self.turnaround_time = None
        self.response_time = None

        