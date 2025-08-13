import random

import simanneal

from job_shop_lib import JobShopInstance, Schedule
from job_shop_lib.exceptions import ValidationError


class JobShopAnnealer(simanneal.Annealer):
    """Helper class for the :class:`SimulatedAnnealingSolver`.

    It uses `simanneal <https://github.com/perrygeo/simanneal>`_ as the
    backend.

    In the context of the job shop scheduling problem, simulated annealing is
    particularly useful for improving previous solutions.

    The process involves iteratively exploring the solution space:

    1. A random move is made to alter the current state. This is done by
       swapping two operations in the sequence of a machine.
    2. The "energy" of the new state is evaluated using an objective function.
       In this case, the energy is calculated as the makespan of the schedule
       plus penalties for any constraint violations (such as deadlines and
       due dates).
    3. The new state is accepted if it has lower energy (a better solution).
       If it has higher energy, it might still be accepted with a certain
       probability, which depends on the current "temperature". The
       temperature decreases over time, reducing the chance of accepting
       worse solutions as the algorithm progresses. This helps to avoid
       getting stuck in local optima.

    This is repeated until the solution converges or a maximum number of
    steps is reached.

    Tuning the annealer is crucial for performance. The base
    ``simanneal.Annealer`` class provides parameters that can be adjusted:

    - ``Tmax``: Maximum (starting) temperature (default: 25000.0).
    - ``Tmin``: Minimum (ending) temperature (default: 2.5).
    - ``steps``: Number of iterations (default: 50000).
    - ``updates``: Number of progress updates (default: 100).

    A good starting point is to set ``Tmax`` to a value that accepts about 98%
    of moves and ``Tmin`` to a value where the solution no longer improves.
    The number of ``steps`` should be large enough to explore the search space
    thoroughly.

    These parameters can be set on the annealer instance. For example:
    ``annealer.Tmax = 12000.0``

    Alternatively, this class provides an ``auto`` method to find reasonable
    parameters based on a desired runtime:
    ``auto_schedule = annealer.auto(minutes=1)``
    ``annealer.set_schedule(auto_schedule)``

    Attributes:
        instance:
            The job shop instance to solve.
        deadline_penalty_factor:
            Factor to penalize deadline violations.
        due_date_penalty_factor:
            Factor to penalize due date violations.
        random_generator:
            Random generator for reproducibility.

    Args:
        instance:
            The job shop instance to solve. It retrieves the jobs and machines
            from the instance and uses them to create the schedule.
        initial_state:
            Initial state of the schedule as a list of lists, where each
            sublist represents the operations of a job.
        deadline_penalty_factor:
            Factor to penalize deadline violations. If a deadline is not met,
            it will add this quantity to the makespan to get the energy
            of the solution.
        due_date_penalty_factor:
            Factor to penalize due date violations. If a due date is not met,
            it will add this quantity to the makespan to get the energy
            of the solution.
        seed:
            Random seed for reproducibility. If ``None``, random behavior will
            be non-deterministic.
    """

    def __init__(
        self,
        instance: JobShopInstance,
        initial_state: list[list[int]],
        deadline_penalty_factor: int = 1_000_000,
        due_date_penalty_factor: int = 100,
        seed: int | None = None,
    ):
        super().__init__(initial_state)
        self.instance = instance
        self.deadline_penalty_factor = deadline_penalty_factor
        self.due_date_penalty_factor = due_date_penalty_factor
        self.random_generator = random.Random(seed)

    def _get_state(self) -> list[list[int]]:
        """Returns the current state of the annealer.

        This method facilitates type checking.
        """
        return self.state

    def move(self) -> None:
        """Generates a neighbor state by swapping two operations."""
        machine_id = self.random_generator.randint(
            0, self.instance.num_machines - 1
        )
        sequence = self._get_state()[machine_id]
        if len(sequence) < 2:
            return

        idx1, idx2 = self.random_generator.sample(range(len(sequence)), 2)
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
        if not self.instance.has_deadlines and not self.instance.has_due_dates:
            return 0.0

        total_penalty = 0.0
        for machine_schedule in schedule.schedule:
            for scheduled_op in machine_schedule:
                violates_deadline = (
                    (scheduled_op.end_time > scheduled_op.operation.deadline)
                    if scheduled_op.operation.deadline is not None
                    else False
                )
                violates_due_date = (
                    (scheduled_op.end_time > scheduled_op.operation.due_date)
                    if scheduled_op.operation.due_date is not None
                    else False
                )
                total_penalty += (
                    violates_deadline * self.deadline_penalty_factor
                    + violates_due_date * self.due_date_penalty_factor
                )
        return total_penalty

    def auto(self, minutes: float, steps: int = 2000) -> dict[str, float]:
        """Explores the search space to determine decent starting temperature
        values for a given time budget.

        Args:
            minutes:
                How long you're willing to wait for results.
            steps:
                The number of steps to take in the exploration process.

        Returns:
            A dictionary suitable for the
            :meth:``simmaneal.Annealer.set_schedule`` method. The dictionary
            contains the following keys: "tmax", "tmin", "steps", "updates".
        """
        assert minutes > 0, "Minutes must be greater than 0"
        return super().auto(minutes, steps)
