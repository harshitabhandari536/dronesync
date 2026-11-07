def fcfs_schedule(tasks):
    tasks = sorted(tasks, key=lambda task: task.arrival_time)

    current_time = 0
    scheduled_tasks = []

    for task in tasks:

        if current_time < task.arrival_time:
            current_time = task.arrival_time

        task.start_time = current_time

        task.waiting_time = (
            task.start_time - task.arrival_time
        )

        current_time += task.burst_time

        task.completion_time = current_time

        task.turnaround_time = (
            task.completion_time - task.arrival_time
        )

        task.response_time = (
            task.start_time - task.arrival_time
        )

        task.status = "COMPLETED"

        scheduled_tasks.append(task)

    return scheduled_tasks