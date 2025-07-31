import random

import simanneal

from job_shop_lib import JobShopInstance, Schedule, ScheduledOperation
from job_shop_lib.exceptions import ValidationError


class JobShopAnnealer(simanneal.Annealer):
    """Simulated Annealing implementation from simanneal API
    for Job Shop Scheduling.

    Attributes:
        instance: The job shop instance to solve.
        initial_state: Initial state of the schedule as a list of lists,
        where each sublist represents the operations of a job.
        penalty_factor: Factor to scale the penalty for infeasible solutions.

    Args:
        instance:
            The job shop instance to solve. It retrieves the jobs and machines
            from the instance and uses them to create the schedule.
        initial_state:
            Initial state of the schedule as a list of lists, where each
            sublist represents the operations of a job.
        penalty_factor:
            Factor to scale the penalty for infeasible solutions. It is used
            to penalize solutions that violate constraints, such as arrival
            times and deadlines. A higher value increases the penalty for
            infeasible solutions, making them less likely to be accepted.
            It is used to calculate the energy of the solution.
            It is used to calculate the makespan of the schedule.
            It is used to calculate the penalties for constraint violations.
    """

    def __init__(
        self,
        instance: JobShopInstance,
        initial_state: list[list[int]],
        penalty_factor: int = 1_000_000,
    ):

        super().__init__(initial_state)
        self.instance = instance
        self.penalty_factor = penalty_factor

    def move(self) -> None:
        """Generates a neighbor state by swapping two operations."""
        machine_id = random.randint(0, self.instance.num_machines - 1)
        sequence = self.state[machine_id]
        if len(sequence) < 2:
            return

        idx1, idx2 = random.sample(range(len(sequence)), 2)
        sequence[idx1], sequence[idx2] = sequence[idx2], sequence[idx1]

    def energy(self) -> float:
        """Computes the makespan with penalties for constraint violations."""
        try:
            schedule = Schedule.from_job_sequences(self.instance, self.state)
            makespan = schedule.makespan()
            penalty = self._compute_penalties(schedule)
            return makespan + penalty
        except ValidationError:
            # If the schedule is invalid, return a large penalty
            return float("inf")

    def _compute_penalties(self, schedule: Schedule) -> float:
        """Calculates penalties for the constraints of
        deadline and arrival time violations."""
        if (
            not self.instance.has_deadlines
            and not self.instance.has_release_dates
        ):
            return 0.0

        job_completion_times = self._get_job_completion_times(schedule)
        penalty = 0.0

        if self.instance.has_deadlines:
            # Use the deadlines_matrix property to get deadlines
            for job_id, completion_time in enumerate(job_completion_times):
                deadlines = self.instance.deadlines_matrix[job_id]
                # Check the last operation's deadline for each job
                last_op_deadline = deadlines[-1]
                if (
                    last_op_deadline is not None
                    and completion_time is not None
                    and completion_time > last_op_deadline
                ):
                    penalty += float(self.penalty_factor) * (
                        completion_time - last_op_deadline
                    )

        if self.instance.has_release_dates:
            arrival_times = self.instance.release_dates_matrix
            for job_id in range(self.instance.num_jobs):
                # Check for the first operation's release date for each job
                first_op_release_date = arrival_times[job_id][0]
                if first_op_release_date is not None:
                    scheduled_op = self._find_scheduled_operation(
                        schedule, job_id, 0
                    )
                    if scheduled_op.start_time < first_op_release_date:
                        penalty += float(self.penalty_factor) * (
                            first_op_release_date - scheduled_op.start_time
                        )

        return penalty

    def _get_job_completion_times(
        self, schedule: Schedule
    ) -> list[int | None]:
        """Returns the completion time of the last operation for each job."""
        completion_times: list[int | None] = [None] * self.instance.num_jobs

        for machine_schedule in schedule.schedule:
            for operation in machine_schedule:
                job_id = operation.job_id
                # Check if this the last operation for this job
                if (
                    operation.position_in_job
                    == self.instance.num_operations - 1
                ):
                    completion_times[job_id] = operation.end_time

        return completion_times

    def _find_scheduled_operation(
        self, schedule: Schedule, job_id: int, operation_index: int
    ) -> ScheduledOperation:
        """Finds the scheduled operation for a given
        job and operation index."""
        for machine_schedule in schedule.schedule:
            for operation in machine_schedule:
                if (
                    operation.job_id == job_id
                    and operation.position_in_job == operation_index
                ):
                    return operation
        raise ValueError(
            f"Scheduled operation not found for job {job_id} and "
            f"operation index {operation_index}"
        )
