from collections.abc import Callable
from job_shop_lib import Schedule


ObjectiveFunction = Callable[[Schedule], float]


def get_makespan_with_penalties_objective(
    deadline_penalty_factor: float = 1_000_000,
    due_date_penalty_factor: float = 100,
) -> ObjectiveFunction:
    """Builds an objective function that returns the makespan plus penalties.

    This factory returns a callable that evaluates a Schedule as the sum of
    its makespan and penalties for violating operation-level deadlines and due
    dates.

    Penalties are applied per scheduled operation that finishes after its
    corresponding attribute value:

    - Deadline violation: adds ``deadline_penalty_factor`` once per violating
      operation (hard constraint surrogate).
    - Due date violation: adds ``due_date_penalty_factor`` once per violating
      operation (soft constraint surrogate).

    Args:
        deadline_penalty_factor:
            Cost added for each operation that
            finishes after its deadline. Defaults to 1_000_000.
        due_date_penalty_factor:
            Cost added for each operation that
            finishes after its due date. Defaults to 100.

    Returns:
        A function ``f(schedule) -> float`` that
        computes ``schedule.makespan() + penalty``.

    Notes:
        - Deadlines and due dates are taken from each operation. If an
          operation does not define the attribute (``None``), no penalty is
          applied for that attribute.
        - If the instance has neither deadlines nor due dates, the objective is
          simply the makespan.
    """

    def objective(schedule: Schedule) -> float:
        makespan = schedule.makespan()
        instance = schedule.instance

        # Fast path: no constraint attributes present in the instance
        if not instance.has_deadlines and not instance.has_due_dates:
            return makespan

        penalty = 0.0
        for machine_schedule in schedule.schedule:
            for scheduled_op in machine_schedule:
                op = scheduled_op.operation
                # Deadline (hard) penalty
                if (
                    op.deadline is not None
                    and scheduled_op.end_time > op.deadline
                ):
                    penalty += deadline_penalty_factor
                # Due date (soft) penalty
                if (
                    op.due_date is not None
                    and scheduled_op.end_time > op.due_date
                ):
                    penalty += due_date_penalty_factor

        return makespan + penalty

    return objective
