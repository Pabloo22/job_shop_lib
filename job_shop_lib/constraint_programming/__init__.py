"""Contains solvers based on Constraint Programming (CP).

CP defines the Job Shop Scheduling Problem through constraints
and focuses on finding a feasible solution. It usually aims to minimize an
objective function, typically the makespan. One of the advantages of these
methods is that they are not restricted to linear constraints.
"""

from job_shop_lib.constraint_programming._ortools_solver import ORToolsSolver

__all__ = [
    "ORToolsSolver",
]
