from job_shop_lib import Operation


def critical_path_lower_bound(
    uncompleted_operations: list[Operation],
    num_machines: int | None = None,
    num_jobs: int | None = None,
) -> int:
    """Computes the critical path lower bound."""

    if num_machines is None:
        num_machines = (
            max(operation.machine_id for operation in uncompleted_operations)
            + 1
        )

    if num_jobs is None:
        num_jobs = (
            max(operation.job_id for operation in uncompleted_operations) + 1
        )

    remaining_machine_times = [0] * num_machines
    remaining_job_times = [0] * num_jobs
    for operation in uncompleted_operations:
        remaining_machine_times[operation.machine_id] += operation.duration
        remaining_job_times[operation.job_id] += operation.duration

    max_machine_time = max(remaining_machine_times)
    max_job_time = max(remaining_job_times)

    lower_bound = max(max_machine_time, max_job_time)

    return lower_bound
