"""Metaheuristic algorithms for solving job shop scheduling problems.

This module provides implementations of various metaheuristic optimization
algorithms designed to solve the job shop scheduling problem.

Metaheuristics are particularly well-suited for JSSP due to their ability to:

- Handle large solution spaces efficiently
- Escape local optima through stochastic mechanisms
- Balance exploration and exploitation of the search space
- Provide good quality solutions within reasonable computational time

Currently implemented algorithms:

- Simulated annealing: A probabilistic technique that accepts worse
  solutions with decreasing probability to escape local optima

The module aims to contain implementations of other
metaheuristic algorithms such as genetic algorithms, particle swarm
optimization, tabu search, etc. Feel free to open an issue if you want to
contribute!

.. autosummary::
    :nosignatures:

    JobShopAnnealer
    SimulatedAnnealingSolver
    NeighborGenerator
    swap_adjacent_operations
    swap_in_critical_path
    swap_random_operations
    ObjectiveFunction
    get_makespan_with_penalties_objective
    compute_penalty_for_deadlines
    compute_penalty_for_due_dates

"""

from job_shop_lib.metaheuristics._objective_functions import (
    ObjectiveFunction,
    get_makespan_with_penalties_objective,
    compute_penalty_for_deadlines,
    compute_penalty_for_due_dates,
)
from job_shop_lib.metaheuristics._neighbor_generators import (
    NeighborGenerator,
    swap_adjacent_operations,
    swap_in_critical_path,
    swap_random_operations,
)
from job_shop_lib.metaheuristics._job_shop_annealer import JobShopAnnealer
from job_shop_lib.metaheuristics._simulated_annealing_solver import (
    SimulatedAnnealingSolver,
)

__all__ = [
    "JobShopAnnealer",
    "SimulatedAnnealingSolver",
    "NeighborGenerator",
    "swap_adjacent_operations",
    "swap_in_critical_path",
    "swap_random_operations",
    "ObjectiveFunction",
    "get_makespan_with_penalties_objective",
    "compute_penalty_for_deadlines",
    "compute_penalty_for_due_dates",
]
