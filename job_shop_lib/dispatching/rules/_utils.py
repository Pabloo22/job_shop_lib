"""Utility functions."""

from typing import Union, List
import time
from collections.abc import Callable
import pandas as pd
from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.exceptions import JobShopLibError
from job_shop_lib.dispatching.rules import DispatchingRuleSolver
from job_shop_lib.dispatching import Dispatcher


def benchmark_dispatching_rules(
    dispatching_rules: Union[
        List[Union[str, Callable[[Dispatcher], Operation]]],
        List[str],
        List[Callable[[Dispatcher], Operation]]
    ],
    instances: List[JobShopInstance],
) -> pd.DataFrame:
    """Benchmark multiple dispatching rules on multiple JobShopInstances.

    This function applies each provided dispatching rule to each given
    :class:`JobShopInstance`, measuring the time taken to solve and the
    makespan of the resulting schedule. It returns a DataFrame summarizing
    the results.

    Args:
        dispatching_rules:
            List of dispatching rules. Each rule can be
            either a string (name of a built-in rule) or a callable
            (custom rule function).
        instances:
            List of :class:`JobShopInstance` objects to be solved.

    Returns:
        A pandas DataFrame with columns:
            - instance: Name of the :class:`JobShopInstance`.
            - rule: Name of the dispatching rule used.
            - time: Time taken to solve the instance (in seconds).
            - makespan: Makespan of the resulting schedule.

    Raises:
        Any exception that might occur during the solving process is caught
        and logged, with None values recorded for time and makespan.

    Example:
        >>> from job_shop_lib.benchmarking import load_benchmark_instance
        >>> instances = [load_benchmark_instance(f"ta{i:02d}")
        ... for i in range(1, 3)]
        >>> rules = ["most_work_remaining", "shortest_processing_time"]
        >>> df = benchmark_dispatching_rules(rules, instances)
        >>> print(df)
          instance                        rule      time  makespan
        0     ta01    shortest_processing_time  0.006492      3439
        1     ta01    most_work_remaining_rule  0.012608      1583
        2     ta02    shortest_processing_time  0.006240      2568
        3     ta02    most_work_remaining_rule  0.012315      1630

    Note:
        - The function handles errors gracefully, allowing the benchmarking
          process to continue even if solving a particular instance fails.
        - For custom rule functions, the function name is used in the
          'rule' column of the output DataFrame.
    """
    results = []

    for instance in instances:
        for rule in dispatching_rules:
            solver = DispatchingRuleSolver(dispatching_rule=rule)

            start_time = time.perf_counter()
            try:
                schedule = solver.solve(instance)
                solve_time = time.perf_counter() - start_time
                makespan = schedule.makespan()

                results.append(
                    {
                        "instance": instance.name,
                        "rule": (
                            rule if isinstance(rule, str) else rule.__name__
                        ),
                        "time": solve_time,
                        "makespan": makespan,
                    }
                )
            except JobShopLibError as e:
                print(f"Error solving {instance.name} with {rule}: {str(e)}")
                results.append(
                    {
                        "instance": instance.name,
                        "rule": (
                            rule if isinstance(rule, str) else rule.__name__
                        ),
                        "time": None,
                        "makespan": None,
                    }
                )

    return pd.DataFrame(results)


# Example usage:
if __name__ == "__main__":
    from job_shop_lib.benchmarking import load_benchmark_instance
    from job_shop_lib.dispatching.rules._dispatching_rules_functions import (
        most_work_remaining_rule,
    )

    # Load instances
    instances_ = [load_benchmark_instance(f"ta{i:02d}") for i in range(1, 3)]

    # Define rules
    rules_: List[str | Callable[[Dispatcher], Operation]] = [
        "most_work_remaining",
        "shortest_processing_time",
        most_work_remaining_rule,
    ]

    # Run benchmark
    df = benchmark_dispatching_rules(rules_, instances_)

    # Display results
    print(df)

    # Group results by rule and compute average makespan and time
    print(df.groupby("rule")[["time", "makespan"]].mean())
