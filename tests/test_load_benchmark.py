from job_shop_lib.benchmarks import (
    load_all_benchmark_instances,
    load_benchmark_instance,
)
from job_shop_lib.solvers import CPSolver


def test_load_benchmark_instance():
    ft06 = load_benchmark_instance("ft06")
    assert ft06.num_jobs == 6
    assert ft06.num_machines == 6

    solution = CPSolver().solve(ft06)
    assert solution.makespan() == ft06.metadata["optimum"] == 55


def test_load_all_benchmark_instances():
    instances = load_all_benchmark_instances()
    assert len(instances) == 162
    assert all(instance.num_jobs > 0 for instance in instances.values())
    assert all(instance.num_machines > 0 for instance in instances.values())

    ft06 = instances["ft06"]
    solution = CPSolver().solve(ft06)
    assert solution.makespan() == ft06.metadata["optimum"] == 55
