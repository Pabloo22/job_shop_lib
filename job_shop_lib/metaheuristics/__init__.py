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
    generate_critical_path_neighbor

"""

from job_shop_lib.metaheuristics._neighbor_generators import (
    NeighborGenerator,
    swap_adjacent_operations,
    swap_in_critical_path,
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
]
