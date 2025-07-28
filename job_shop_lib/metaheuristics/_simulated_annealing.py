import random
import logging
from typing import Any, Sequence

try:
    from simanneal import Annealer
except ImportError:
    raise ImportError(
        "simanneal library is required for SimulatedAnnealingSolver. "
        "Install with: pip install simanneal"
    )

from job_shop_lib import JobShopInstance, Schedule
from job_shop_lib import Schedule as ScheduleBuilder
from job_shop_lib import ValidationError


class JobShopAnnealer(Annealer):
    """Simulated Annealing implementation from simanneal API
    for Job Shop Scheduling."""

    def __init__(
        self,
        instance: JobShopInstance,
        initial_state: list[list[int]],
        penalty_factor: int = 1_000_000,
    ):
        """Initializes the annealer with a job shop instance and an initial state.

        Args:
            instance: The job shop instance to solve.
            initial_state: Initial state of the schedule as a list of lists,
                where each sublist represents the operations of a job.
            penalty_factor: Factor to scale the penalty for infeasible solutions.
        """

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
            schedule = ScheduleBuilder.from_job_sequences(
                self.instance, self.state
            )
            makespan = schedule.makespan()
            penalty = self._compute_penalties(schedule)
            return makespan + penalty
        except ValidationError as e:
            # If the schedule is invalid, return a large penalty
            logging.warning("Invalid schedule encountered: %s", e)
            return float("inf")

    def _compute_penalties(self, schedule: Schedule) -> float:
        """Calculates penalties for the constraints of deadline and arrival time violations."""
        if not hasattr(self.instance, "deadlines") and not hasattr(
            self.instance, "arrival_times"
        ):
            return 0.0

        job_completion_times = self._get_job_completion_times(schedule)
        penalty = 0.0

        if hasattr(self.instance, "deadlines"):
            deadlines = self.instance.deadlines
            for job_id, completion_time in enumerate(job_completion_times):
                if completion_time > deadlines[job_id]:
                    penalty += self.penalty_factor * (
                        completion_time - deadlines[job_id]
                    )
