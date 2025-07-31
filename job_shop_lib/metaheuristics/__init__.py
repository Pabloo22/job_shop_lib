"""Metaheuristic algorithms for solving job shop scheduling problems.

This module provides implementations of various metaheuristic optimization
algorithms designed to solve Job Shop Scheduling Problems (JSSP). These
algorithms are nature-inspired or probabilistic techniques that can find
near-optimal solutions for complex combinatorial optimization problems.

Metaheuristics are particularly well-suited for JSSP due to their ability to:

- Handle large solution spaces efficiently
- Escape local optima through stochastic mechanisms
- Balance exploration and exploitation of the search space
- Provide good quality solutions within reasonable computational time

Currently implemented algorithms:
- Simulated Annealing (SA): A probabilistic technique that accepts worse
solutions with decreasing probability to escape local optima

The module is designed to be extensible for future implementations of other
metaheuristic algorithms such as Genetic Algorithms, Particle Swarm
Optimization, Tabu Search, and other nature-inspired optimization techniques.

.. autosummary::
    JobShopAnnealer: Simulated annealing implementation for JSSP optimization
    SimulatedAnnealingSolver: Solver interface for simulated annealing
    algorithm
"""

from job_shop_lib.metaheuristics._job_shop_annealer import JobShopAnnealer
from job_shop_lib.metaheuristics._simulated_annealing_solver import (
    SimulatedAnnealingSolver,
)

__all__ = [
    "JobShopAnnealer",
    "SimulatedAnnealingSolver",
]
