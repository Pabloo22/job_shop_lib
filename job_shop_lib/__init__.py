"""Contains the main data structures and base classes.

.. autosummary::
    :nosignatures:

    Operation
    JobShopInstance
    ScheduledOperation
    Schedule
    Solver
    BaseSolver

"""

from job_shop_lib._operation import Operation
from job_shop_lib._job_shop_instance import JobShopInstance
from job_shop_lib._scheduled_operation import ScheduledOperation
from job_shop_lib._schedule import Schedule
from job_shop_lib._base_solver import BaseSolver, Solver


__version__ = "1.0.0-b.3"

__all__ = [
    "Operation",
    "JobShopInstance",
    "ScheduledOperation",
    "Schedule",
    "Solver",
    "BaseSolver",
    "__version__",
]
