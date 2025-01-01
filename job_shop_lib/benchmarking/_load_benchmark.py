"""Contains functions to load benchmark instances from a JSON file."""

from typing import Any, Dict

import functools
import json
from importlib import resources

from job_shop_lib import JobShopInstance


@functools.cache
def load_all_benchmark_instances() -> Dict[str, JobShopInstance]:
    """Loads all benchmark instances available.

    Returns:
        A dictionary containing the names of the benchmark instances as keys
        and the corresponding :class:`JobShopInstance` objects as values.

    """
    benchmark_instances_dict = load_benchmark_json()
    return {
        name: load_benchmark_instance(name)
        for name in benchmark_instances_dict
    }


def load_benchmark_instance(name: str) -> JobShopInstance:
    """Loads a specific benchmark instance.

    Calls to :func:`load_benchmark_json` to load the benchmark instances from
    the JSON file. The instance is then loaded from the dictionary using the
    provided name. Since `load_benchmark_json` is cached, the file is only
    read once.

    Args:
        name: The name of the benchmark instance to load. Can be one of the
            following: "abz5-9", "ft06", "ft10", "ft20", "la01-40", "orb01-10",
            "swb01-20", "yn1-4", or "ta01-80".
    """
    benchmark_dict = load_benchmark_json()[name]
    return JobShopInstance.from_matrices(
        duration_matrix=benchmark_dict["duration_matrix"],
        machines_matrix=benchmark_dict["machines_matrix"],
        name=name,
        metadata=benchmark_dict["metadata"],
    )


@functools.cache
def load_benchmark_json() -> Dict[str, Dict[str, Any]]:
    """Loads the raw JSON file containing the benchmark instances.

    Results are cached to avoid reading the file multiple times.

    Each instance is represented as a dictionary with the following keys
    and values:

    * ``name`` (``str``): The name of the instance.
    * ``duration_matrix`` (``list[list[int]]``): The matrix containing the
      durations for each operation.
    * ``machines_matrix`` (``list[list[int]]``): The matrix containing the
      machines for each operation.
    * ``metadata`` (``dict[str, Any]``): A dictionary containing metadata
      about the instance. The keys are:

      * ``optimum`` (``int | None``)
      * ``lower_bound`` (``int``)
      * ``upper_bound`` (``int``)
      * ``reference`` (``str``)

    Note:
        This dictionary is the standard way to represent instances in
        JobShopLib. You can obtain the dictionary of each instance with
        :class:`~job_shop_lib.JobShopInstance`'s
        :meth:`~job_shop_lib.JobShopInstance.to_dict` method.

    Returns:
        The dictionary containing the benchmark instances represented as
        dictionaries.
    """
    benchmark_file = (
        resources.files("job_shop_lib.benchmarking")
        / "benchmark_instances.json"
    )

    with benchmark_file.open("r", encoding="utf-8") as f:
        return json.load(f)
