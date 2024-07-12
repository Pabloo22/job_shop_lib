"""Contains functions to load benchmark instances.

.. autosummary::

    load_all_benchmark_instances
    load_benchmark_instance
    load_benchmark_json

You can load a benchmark instance from the library:

.. code-block:: python

    from job_shop_lib.benchmarking import load_benchmark_instance

    ft06 = load_benchmark_instance("ft06")


This package contains functions to load the instances from the file
and return them as :class:`JobShopInstance` objects without having to download
them manually.

The contributions to this benchmark dataset are as follows:

- ``abz5-9``: by Adams et al. (1988).

- ``ft06``, ``ft10``, ``ft20``: by Fisher and Thompson (1963).

- ``la01-40``: by Lawrence (1984)

- ``orb01-10``: by Applegate and Cook (1991).

- ``swb01-20``: by Storer et al. (1992).

- ``yn1-4``: by Yamada and Nakano (1992).

- ``ta01-80``: by Taillard (1993).

The metadata from these instances has been updated using data from:
https://github.com/thomasWeise/jsspInstancesAndResults

It includes the following information:
    - "optimum" (``int | None``): The optimal makespan for the instance.
    - "lower_bound" (``int``): The lower bound for the makespan. If
      optimality is known, it is equal to the optimum.
    - "upper_bound" (``int``): The upper bound for the makespan. If
      optimality is known, it is equal to the optimum.
    - "reference" (``str``): The paper or source where the instance was first
      introduced.

.. code-block:: python

    >>> ft06.metadata
    {'optimum': 55,
    'upper_bound': 55,
    'lower_bound': 55,
    'reference': "J.F. Muth, G.L. Thompson. 'Industrial scheduling.',
    Englewood Cliffs, NJ, Prentice-Hall, 1963."}

References:

    - J. Adams, E. Balas, and D. Zawack, "The shifting bottleneck procedure
      for job shop scheduling," Management Science, vol. 34, no. 3,
      pp. 391–401, 1988.

    - J.F. Muth and G.L. Thompson, Industrial scheduling. Englewood Cliffs,
      NJ: Prentice-Hall, 1963.

    - S. Lawrence, "Resource constrained project scheduling: An experimental
      investigation of heuristic scheduling techniques (Supplement),"
      Carnegie-Mellon University, Graduate School of Industrial
      Administration, Pittsburgh, Pennsylvania, 1984.

    - D. Applegate and W. Cook, "A computational study of job-shop
      scheduling," ORSA Journal on Computer, vol. 3, no. 2, pp. 149–156,
      1991.

    - R.H. Storer, S.D. Wu, and R. Vaccari, "New search spaces for
      sequencing problems with applications to job-shop scheduling,"
      Management Science, vol. 38, no. 10, pp. 1495–1509, 1992.

    - T. Yamada and R. Nakano, "A genetic algorithm applicable to
      large-scale job-shop problems," in Proceedings of the Second
      International Workshop on Parallel Problem Solving from Nature
      (PPSN'2), Brussels, Belgium, pp. 281–290, 1992.

    - E. Taillard, "Benchmarks for basic scheduling problems," European
      Journal of Operational Research, vol. 64, no. 2, pp. 278–285, 1993.

"""

from job_shop_lib.benchmarking._load_benchmark import (
    load_all_benchmark_instances,
    load_benchmark_instance,
    load_benchmark_json,
)

__all__ = [
    "load_all_benchmark_instances",
    "load_benchmark_instance",
    "load_benchmark_json",
]
