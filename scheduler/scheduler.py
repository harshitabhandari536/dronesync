
class Scheduler:

    def __init__(self):
        self.ready_queue = []
        self.running_task = None
        self.completed_tasks = []

        self.algorithm = "FCFS"
        self.time_quantum = 2
        self.quantum_used = 0

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        self.quantum_used = 0

    def set_time_quantum(self, quantum):
        if quantum < 1:
            raise ValueError("Time quantum must be at least 1.")

        self.time_quantum = quantum

    def add_task(self, task):
        self.ready_queue.append(task)

    def get_ready_queue(self):
        return self.ready_queue

    def clear_queue(self):
        self.ready_queue.clear()

    def reassign_pending_tasks(self, failed_drone_id, new_drone_id):
        """
        Reassign tasks in the ready queue from a failed drone
        to another available drone.
        """
        reassigned_tasks = []

        for task in self.ready_queue:
            if task.drone_id == failed_drone_id:
                task.drone_id = new_drone_id
                reassigned_tasks.append(task)

        return reassigned_tasks

    def get_next_task(self):

        if not self.ready_queue:
            return None

        if self.algorithm == "FCFS":
            task = min(
                self.ready_queue,
                key=lambda task: (
                    task.arrival_time,
                    task.task_id
                )
            )

        elif self.algorithm == "Priority":
            task = min(
                self.ready_queue,
                key=lambda task: (
                    task.priority,
                    task.arrival_time,
                    task.task_id
                )
            )

        elif self.algorithm == "Round Robin":
            task = self.ready_queue[0]

        else:
            task = self.ready_queue[0]

        self.ready_queue.remove(task)

        return task

    def start_next_task(self, current_time):

        if self.running_task is not None:
            return self.running_task

        next_task = self.get_next_task()

        if next_task is None:
            return None

        self.running_task = next_task
        next_task.status = "RUNNING"

        if next_task.start_time is None:
            next_task.start_time = current_time
            next_task.response_time = (
                current_time - next_task.arrival_time
            )

        self.quantum_used = 0

        return next_task

    def execute_current_task(self, current_time):

        if self.running_task is None:
            return None

        task = self.running_task

        task.remaining_burst_time -= 1
        self.quantum_used += 1

        if task.remaining_burst_time <= 0:

            task.completion_time = current_time

            task.turnaround_time = (
                task.completion_time - task.arrival_time
            )

            task.waiting_time = (
                task.turnaround_time - task.original_burst_time
            )

            task.status = "COMPLETED"

            self.completed_tasks.append(task)

            self.running_task = None
            self.quantum_used = 0

            return task

        if (
            self.algorithm == "Round Robin"
            and self.quantum_used >= self.time_quantum
        ):

            task.status = "READY"
            self.ready_queue.append(task)

            self.running_task = None
            self.quantum_used = 0

        return None
