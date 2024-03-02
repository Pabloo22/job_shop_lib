from typing import Any

import functools
import json
from importlib import resources

from job_shop_lib import JobShopInstance


def load_all_benchmark_instances() -> dict[str, JobShopInstance]:
    benchmark_instances_dict = load_benchmark_json()
    return {
        name: load_benchmark_instance(name)
        for name in benchmark_instances_dict
    }


def load_benchmark_instance(name: str) -> JobShopInstance:
    benchmark_dict = load_benchmark_json()[name]
    return JobShopInstance.from_matrices(
        duration_matrix=benchmark_dict["duration_matrix"],
        machines_matrix=benchmark_dict["machines_matrix"],
        name=name,
        metadata=benchmark_dict["metadata"],
    )


@functools.cache
def load_benchmark_json() -> dict[str, dict[str, Any]]:
    benchmark_file = (
        resources.files("job_shop_lib.benchmarks") / "benchmark_instances.json"
    )

    with benchmark_file.open("r", encoding="utf-8") as f:
        return json.load(f)
