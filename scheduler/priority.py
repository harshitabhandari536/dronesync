def priority_schedule(tasks):
    remaining_tasks = tasks.copy()

    current_time = 0
    scheduled_tasks = []

    while remaining_tasks:

        available_tasks = [
            task
            for task in remaining_tasks
            if task.arrival_time <= current_time
        ]

        if not available_tasks:
            current_time = min(
                task.arrival_time
                for task in remaining_tasks
            )
            continue

        selected_task = min(
            available_tasks,
            key=lambda task: (task.priority, task.arrival_time)
        )

        selected_task.start_time = current_time

        selected_task.waiting_time = (
            selected_task.start_time
            - selected_task.arrival_time
        )

        current_time += selected_task.burst_time

        selected_task.completion_time = current_time

        selected_task.turnaround_time = (
            selected_task.completion_time
            - selected_task.arrival_time
        )

        selected_task.response_time = (
            selected_task.start_time
            - selected_task.arrival_time
        )

        selected_task.status = "COMPLETED"

        scheduled_tasks.append(selected_task)
        remaining_tasks.remove(selected_task)

    return scheduled_tasks