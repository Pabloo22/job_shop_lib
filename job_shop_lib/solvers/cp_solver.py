from __future__ import annotations

from typing import Optional
import time

from ortools.sat.python import cp_model

from job_shop_lib import (
    JobShopInstance,
    Schedule,
    ScheduledOperation,
    Operation,
)
from job_shop_lib.solvers import NoSolutionFound


class CPSolver:
    def __init__(
        self,
        log_search_progress: bool = False,
        time_limit: Optional[float] = None,
    ):
        self.log_search_progress = log_search_progress
        self.time_limit = time_limit

        self.makespan = None
        self.model = None
        self.solver = None
        self.operations_start = {}

    def initialize_model(self, instance: JobShopInstance):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.log_search_progress = self.log_search_progress
        if self.time_limit is not None:
            self.solver.parameters.max_time_in_seconds = self.time_limit
        self._create_variables(instance)
        self._add_constraints(instance)
        self._set_objective(instance)

    def solve(self, instance: JobShopInstance) -> Schedule:
        """Creates the variables, constraints and objective, and solves the
        problem.

        If a solution is found, it extracts and returns the start times of
        each operation and the makespan. If no solution is found, it raises
        a NoSolutionFound exception.
        """
        self.initialize_model(instance)

        start_time = time.perf_counter()
        status = self.solver.Solve(self.model)
        elapsed_time = time.perf_counter() - start_time

        if not status in {cp_model.OPTIMAL, cp_model.FEASIBLE}:
            msg = (
                f"No solution could be found for the given problem. "
                f"Elapsed time: {elapsed_time} seconds."
            )
            raise NoSolutionFound(msg)

        metadata = {
            "status": "optimal" if status == cp_model.OPTIMAL else "feasible",
            "elapsed_time": elapsed_time,
            "makespan": self.solver.Value(self.makespan),
        }
        return self._create_schedule(instance, metadata)

        # if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        #     # Retrieve solution
        #     solution = {
        #         op_id: self.solver.Value(start_var)
        #         for op_id, (start_var, _) in self.operations_start.items()
        #     }
        #     solution["makespan"] = self.solver.Value(self.makespan)
        #     solution["elapsed_time"] = elapsed_time
        #     status = "optimal" if status == cp_model.OPTIMAL else "feasible"
        #     solution["status"] = status
        #     return solution

    def __call__(self, instance: JobShopInstance) -> Schedule:
        return self.solve(instance)

    def _create_schedule(
        self, instance: JobShopInstance, metadata: dict[str, float | str]
    ) -> Schedule:
        """Creates a Schedule object from the solution."""
        operations_start = {
            op_id: self.solver.Value(start_var)
            for op_id, (start_var, _) in self.operations_start.items()
        }

        unsorted_schedule = [[] for _ in range(instance.num_machines)]
        for op_id, start_time in operations_start.items():
            job_id = Operation.get_job_id_from_id(op_id)
            position = Operation.get_position_from_id(op_id)
            operation = instance.jobs[job_id][position]
            unsorted_schedule[operation.machine_id].append(
                ScheduledOperation(operation, start_time, operation.machine_id)
            )

        sorted_schedule = [
            sorted(scheduled_operation, key=lambda x: x.start_time)
            for scheduled_operation in unsorted_schedule
        ]

        return Schedule(sorted_schedule, metadata)

    def _create_variables(self, instance: JobShopInstance):
        """Creates two variables for each operation: start and end time."""
        for j, job in enumerate(instance.jobs):
            for p, operation in enumerate(job):
                op_id = operation.get_id(j, p)
                start_var = self.model.NewIntVar(
                    0, instance.total_duration, f"start_{op_id}"
                )
                end_var = self.model.NewIntVar(
                    0, instance.total_duration, f"end_{op_id}"
                )
                self.operations_start[op_id] = (start_var, end_var)
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

    def _add_job_constraints(self, instance: JobShopInstance):
        """Adds job constraints to the model. Operations within a job must be
        performed in sequence. If operation A must precede operation B in a
        job, we ensure A's end time is less than or equal to B's start time."""
        for job_id, job in enumerate(instance.jobs):
            for position in range(1, len(job)):
                self.model.Add(
                    self.operations_start[
                        job[position - 1].get_id(job_id, position - 1)
                    ][1]
                    <= self.operations_start[
                        job[position].get_id(job_id, position)
                    ][0]
                )

    def _add_machine_constraints(self, instance: JobShopInstance):
        """Adds machine constraints to the model. Operations assigned to the
        same machine cannot overlap. This is ensured by creating interval
        variables (which represent the duration an operation occupies a
        machine) and adding a 'no overlap' constraint for these intervals on
        each machine."""

        # Create interval variables for each operation on each machine
        machines_operations = [[] for _ in range(instance.num_machines)]
        for j, job in enumerate(instance.jobs):
            for p, operation in enumerate(job):
                machines_operations[operation.machine_id].append(
                    (
                        self.operations_start[operation.get_id(j, p)],
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

    def _set_objective(self, instance: JobShopInstance):
        """The objective is to minimize the makespan, which is the total
        duration of the schedule."""
        self.makespan = self.model.NewIntVar(
            0, instance.total_duration, "makespan"
        )
        end_times = [end for _, end in self.operations_start.values()]
        self.model.AddMaxEquality(self.makespan, end_times)
        self.model.Minimize(self.makespan)


# if __name__ == "__main__":
#     from gnn_scheduler.job_shop import load_from_benchmark

#     instance = load_from_benchmark("swv10")
#     solver = CPSolver(instance, time_limit=1)
#     solution_ = solver.solve()
#     print(solution_)
