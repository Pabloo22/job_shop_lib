import json
from importlib import resources

from job_shop_lib import JobShopInstance


with resources.path(
    "job_shop_lib.benchmarks", "benchmark_instances.json"
) as path:
    with open(path, "r", encoding="utf-8") as f:
        BENCHMARK_INSTANCES_DICT = json.load(f)


def load_all_benchmark_instances() -> dict[str, JobShopInstance]:
    return {
        name: load_benchmark_instance(name)
        for name in BENCHMARK_INSTANCES_DICT
    }


def load_benchmark_instance(name: str) -> JobShopInstance:
    benchmark_dict = BENCHMARK_INSTANCES_DICT[name]

    return JobShopInstance.from_matrices(
        duration_matrix=benchmark_dict["duration_matrix"],
        machines_matrix=benchmark_dict["machines_matrix"],
        name=name,
        metadata=benchmark_dict["metadata"],
    )
