"""
Contains the implementation of the JobShopAnnealer class,
which is a simulated annealing algorithm for solving job
shop scheduling problems.

SA (Simulated Annealing) is a probabilistic technique (metaheuristic
algorithm) for approximating the global optimum of a given function.
It seeks to find a good approximation of the optimized makespan
by exploring the schedule space and accepting worse schedules with
evaluating the metropolis criterion. It represents the JSSP solution by
defining the objective function that complies with the constraints of the
arrival times and deadlines.
"""

from job_shop_lib.metaheuristics._job_shop_annealer import JobShopAnnealer

__all__ = [
    "JobShopAnnealer",
]
