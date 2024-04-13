"""Type hint for all solvers."""

from typing import Callable

from job_shop_lib import JobShopInstance, Schedule


Solver = Callable[[JobShopInstance], Schedule]
