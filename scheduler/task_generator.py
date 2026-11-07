from scheduler.task import Task


class TaskGenerator:

    def __init__(self):
        self.task_counter = 1

    def create_task(self, drone, current_time):

        task_id = f"T{self.task_counter:03d}"

        
        priority = ((self.task_counter - 1) % 3) + 1

        task = Task(
            task_id=task_id,
            drone_id=drone.drone_id,
            arrival_time=current_time,
            burst_time=3,
            priority=priority
        )

        self.task_counter += 1

        return task