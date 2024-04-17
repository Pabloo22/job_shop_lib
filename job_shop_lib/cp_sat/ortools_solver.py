"""Home of the ORToolsSolver class."""

from __future__ import annotations

import time

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar

from job_shop_lib import (
    JobShopInstance,
    Schedule,
    ScheduledOperation,
    Operation,
)
from job_shop_lib import NoSolutionFoundError, BaseSolver


class ORToolsSolver(BaseSolver):
    """A solver for the job shop scheduling problem using constraint
    programming.

    This solver uses the ortools library to solve the job shop scheduling
    problem using constraint programming.
    """

    def __init__(
        self,
        max_time_in_seconds: float | None = None,
        log_search_progress: bool = False,
    ):
        self.log_search_progress = log_search_progress
        self.max_time_in_seconds = max_time_in_seconds

        self.makespan: cp_model.IntVar | None = None
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self._operations_start: dict[Operation, tuple[IntVar, IntVar]] = {}

    def __call__(self, instance: JobShopInstance) -> Schedule:
        # Re-defined here since we already add metadata to the schedule in
        # the solve method.
        return self.solve(instance)

    def solve(self, instance: JobShopInstance) -> Schedule:
        """Creates the variables, constraints and objective, and solves the
        problem.

        If a solution is found, it extracts and returns the start times of
        each operation and the makespan. If no solution is found, it raises
        a NoSolutionFound exception.
        """
        self._initialize_model(instance)

        start_time = time.perf_counter()
        status = self.solver.Solve(self.model)
        elapsed_time = time.perf_counter() - start_time

        if status not in {cp_model.OPTIMAL, cp_model.FEASIBLE}:
            raise NoSolutionFoundError(
                f"No solution could be found for the given problem. "
                f"Elapsed time: {elapsed_time} seconds."
            )
        if self.makespan is None:
            # Check added to satisfy mypy
            raise ValueError("The makespan variable was not set.")

        metadata = {
            "status": "optimal" if status == cp_model.OPTIMAL else "feasible",
            "elapsed_time": elapsed_time,
            "makespan": self.solver.Value(self.makespan),
            "solved_by": "ORToolsSolver",
        }
        return self._create_schedule(instance, metadata)

    def _initialize_model(self, instance: JobShopInstance):
        """Initializes the model with variables, constraints and objective.

        The model is initialized with two variables for each operation: start
        and end time. The constraints ensure that operations within a job are
        performed in sequence and that operations assigned to the same machine
        do not overlap. The objective is to minimize the makespan.

        Args:
            instance: The job shop instance to be solved.
        """
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.log_search_progress = self.log_search_progress
        self._operations_start = {}
        if self.max_time_in_seconds is not None:
            self.solver.parameters.max_time_in_seconds = (
                self.max_time_in_seconds
            )
        self._create_variables(instance)
        self._add_constraints(instance)
        self._set_objective(instance)

    def _create_schedule(
        self, instance: JobShopInstance, metadata: dict[str, object]
    ) -> Schedule:
        """Creates a Schedule object from the solution."""
        operations_start: dict[Operation, int] = {
            operation: self.solver.Value(start_var)
            for operation, (start_var, _) in self._operations_start.items()
        }

        unsorted_schedule: list[list[ScheduledOperation]] = [
            [] for _ in range(instance.num_machines)
        ]
        for operation, start_time in operations_start.items():
            unsorted_schedule[operation.machine_id].append(
                ScheduledOperation(operation, start_time, operation.machine_id)
            )

        sorted_schedule = [
            sorted(scheduled_operation, key=lambda x: x.start_time)
            for scheduled_operation in unsorted_schedule
        ]

        return Schedule(
            instance=instance, schedule=sorted_schedule, **metadata
        )

    def _create_variables(self, instance: JobShopInstance):
        """Creates two variables for each operation: start and end time."""
        for job in instance.jobs:
            for operation in job:
                start_var = self.model.NewIntVar(
                    0, instance.total_duration, f"start_{operation}"
                )
                end_var = self.model.NewIntVar(
                    0, instance.total_duration, f"end_{operation}"
                )
                self._operations_start[operation] = (start_var, end_var)
                self.model.Add(end_var == start_var + operation.duration)

    def _add_constraints(self, instance: JobShopInstance):
        """Adds job and machine constraints.

        Job Constraints: Ensure that operations within a job are performed in
        sequence. If operation A must precede operation B in a job, we ensure
        A's end time is less than or equal to B's start time.

        Machine Constraints: Operations assigned to the same machine cannot
        overlap. This is ensured by creating interval variables (which
        represent the duration an operation occupies a machine)
        and adding a 'no overlap' constraint for these intervals on
        each machine.
        """
        self._add_job_constraints(instance)
        self._add_machine_constraints(instance)

    def _set_objective(self, instance: JobShopInstance):
        """The objective is to minimize the makespan, which is the total
        duration of the schedule."""
        self.makespan = self.model.NewIntVar(
            0, instance.total_duration, "makespan"
        )
        end_times = [end for _, end in self._operations_start.values()]
        self.model.AddMaxEquality(self.makespan, end_times)
        self.model.Minimize(self.makespan)

    def _add_job_constraints(self, instance: JobShopInstance):
        """Adds job constraints to the model. Operations within a job must be
        performed in sequence. If operation A must precede operation B in a
        job, we ensure A's end time is less than or equal to B's start time."""
        for job in instance.jobs:
            for position in range(1, len(job)):
                self.model.Add(
                    self._operations_start[job[position - 1]][1]
                    <= self._operations_start[job[position]][0]
                )

    def _add_machine_constraints(self, instance: JobShopInstance):
        """Adds machine constraints to the model. Operations assigned to the
        same machine cannot overlap. This is ensured by creating interval
        variables (which represent the duration an operation occupies a
        machine) and adding a 'no overlap' constraint for these intervals on
        each machine."""

        # Create interval variables for each operation on each machine
        machines_operations: list[list[tuple[tuple[IntVar, IntVar], int]]] = [
            [] for _ in range(instance.num_machines)
        ]
        for job in instance.jobs:
            for operation in job:
                machines_operations[operation.machine_id].append(
                    (
                        self._operations_start[operation],
                        operation.duration,
                    )
                )
        for machine_id, operations in enumerate(machines_operations):
            intervals = []
            for (start_var, end_var), duration in operations:
                interval_var = self.model.NewIntervalVar(
                    start_var, duration, end_var, f"interval_{machine_id}"
                )
                intervals.append(interval_var)
            self.model.AddNoOverlap(intervals)
