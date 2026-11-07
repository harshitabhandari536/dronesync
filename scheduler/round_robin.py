from collections import deque


def round_robin_schedule(tasks, time_quantum):
    remaining_tasks = tasks.copy()

    remaining_tasks.sort(key=lambda task: task.arrival_time)

    ready_queue = deque()

    current_time = 0
    index = 0
    scheduled_tasks = []

    while ready_queue or index < len(remaining_tasks):

        if not ready_queue and current_time < remaining_tasks[index].arrival_time:
            current_time = remaining_tasks[index].arrival_time

        while (
            index < len(remaining_tasks)
            and remaining_tasks[index].arrival_time <= current_time
        ):
            ready_queue.append(remaining_tasks[index])
            index += 1

        task = ready_queue.popleft()

        if task.start_time is None:
            task.start_time = current_time
            task.response_time = (
                task.start_time - task.arrival_time
            )

        execution_time = min(
            time_quantum,
            task.burst_time
        )

        current_time += execution_time
        task.burst_time -= execution_time

        while (
            index < len(remaining_tasks)
            and remaining_tasks[index].arrival_time <= current_time
        ):
            ready_queue.append(remaining_tasks[index])
            index += 1

        if task.burst_time > 0:
            ready_queue.append(task)
        else:
            task.completion_time = current_time

            task.turnaround_time = (
                task.completion_time
                - task.arrival_time
            )

            task.waiting_time = (
                task.turnaround_time
                - task.original_burst_time
            )

            task.status = "COMPLETED"

            scheduled_tasks.append(task)

    return scheduled_tasks