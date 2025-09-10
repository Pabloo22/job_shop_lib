from job_shop_lib import JobShopInstance
from job_shop_lib.benchmarking import (
    load_all_benchmark_instances,
    load_benchmark_instance,
    load_benchmark_group,
)
from job_shop_lib.constraint_programming import ORToolsSolver


def test_load_benchmark_instance():
    ft06 = load_benchmark_instance("ft06")
    assert ft06.num_jobs == 6
    assert ft06.num_machines == 6

    solution = ORToolsSolver().solve(ft06)
    assert solution.makespan() == ft06.metadata["optimum"] == 55
    ft06_from_file = JobShopInstance.from_taillard_file("./tests/ft06.txt")
    assert ft06 == ft06_from_file
    assert ft06.name == ft06_from_file.name


def test_load_all_benchmark_instances():
    instances = load_all_benchmark_instances()
    assert len(instances) == 162
    assert all(instance.num_jobs > 0 for instance in instances.values())
    assert all(instance.num_machines > 0 for instance in instances.values())

    ft06 = instances["ft06"]
    solution = ORToolsSolver().solve(ft06)
    assert solution.makespan() == ft06.metadata["optimum"] == 55


def test_load_benchmark_group_la():
    la_instances = load_benchmark_group("la")
    assert len(la_instances) == 40  # la01-la40
    assert all(isinstance(inst, JobShopInstance) for inst in la_instances)
    assert all(inst.name.startswith("la") for inst in la_instances)
    # Cached call returns same list object (functools.cache behavior)
    assert load_benchmark_group("la") is la_instances


def test_load_benchmark_group_ft():
    ft_instances = load_benchmark_group("ft")
    assert len(ft_instances) == 3  # ft06, ft10, ft20
    names = {inst.name for inst in ft_instances}
    assert names == {"ft06", "ft10", "ft20"}


def test_load_benchmark_group_nonexistent():
    none = load_benchmark_group("zz")
    assert none == []
