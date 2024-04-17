"""Package for loading benchmark instances.

All benchmark instances are stored in a single JSON file. This module provides
functions to load the instances from the file and return them as
JobShopInstance objects.

The contributions to this benchmark dataset are as follows:

abz5-9: This subset, comprising five instances, was introduced by Adams et
    al. (1988).
ft06, ft10, ft20: These three instances are attributed to the work of
    Fisher and Thompson, as detailed in their 1963 work.
la01-40: A collection of forty instances, this group was contributed by
    Lawrence, as referenced in his 1984 report.
orb01-10: Ten instances in this category were provided by Applegate and
    Cook, as seen in their 1991 study.
swb01-20: This segment, encompassing twenty instances, was contributed by
    Storer et al., as per their 1992 article.
yn1-4: Yamada and Nakano are credited with the addition of four instances
    in this group, as found in their 1992 paper.
ta01-80: The largest contribution, consisting of eighty instances, was
    made by Taillard, as documented in his 1993 paper.

The metadata from these instances has been updated using data from:

Thomas Weise. jsspInstancesAndResults. Accessed in January 2024.
Available at: https://github.com/thomasWeise/jsspInstancesAndResults

It includes the following information:
    - "optimum" (int | None): The optimal makespan for the instance.
    - "lower_bound" (int): The lower bound for the makespan. If
        optimality is known, it is equal to the optimum.
    - "upper_bound" (int): The upper bound for the makespan. If
        optimality is known, it is equal to the optimum.
    - "reference" (str): The paper or source where the instance was first
        introduced.

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

from job_shop_lib.benchmarking.load_benchmark import (
    load_all_benchmark_instances,
    load_benchmark_instance,
    load_benchmark_json,
)

__all__ = [
    "load_all_benchmark_instances",
    "load_benchmark_instance",
    "load_benchmark_json",
]
