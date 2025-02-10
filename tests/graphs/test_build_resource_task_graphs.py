from job_shop_lib.graphs._build_resource_task_graphs import (
    build_complete_resource_task_graph,
    build_resource_task_graph_with_jobs,
    build_resource_task_graph,
)
from job_shop_lib import JobShopInstance
from job_shop_lib.benchmarking import load_all_benchmark_instances


def test_expected_num_nodes_complete():
    benchmark_instances = load_all_benchmark_instances()
    for instance in list(benchmark_instances.values())[:10]:
        graph = build_complete_resource_task_graph(instance)
        expected_num_nodes = get_expected_num_nodes_for_complete_graph(
            instance
        )
        assert len(graph.nodes) == expected_num_nodes


def test_expected_num_nodes_with_jobs():
    benchmark_instances = load_all_benchmark_instances()
    for instance in list(benchmark_instances.values())[:10]:
        graph = build_resource_task_graph_with_jobs(instance)
        expected_num_nodes = get_expected_num_nodes_for_graph_with_jobs(
            instance
        )
        assert len(graph.nodes) == expected_num_nodes


def test_expected_num_nodes():
    benchmark_instances = load_all_benchmark_instances()
    for instance in list(benchmark_instances.values())[:10]:
        graph = build_resource_task_graph(instance)
        expected_num_nodes = get_expected_num_nodes(instance)
        assert len(graph.nodes) == expected_num_nodes


def test_expected_num_edges_complete():
    benchmark_instances = load_all_benchmark_instances()
    for instance in list(benchmark_instances.values())[:10]:
        graph = build_complete_resource_task_graph(instance)
        expected_num_edges = get_expected_num_edges_for_complete_graph(
            instance
        )
        assert graph.num_edges == expected_num_edges


def test_expected_num_edges_complete_example(example_job_shop_instance):
    graph = build_complete_resource_task_graph(example_job_shop_instance)
    expected_num_edges = get_expected_num_edges_for_complete_graph(
        example_job_shop_instance
    )
    assert graph.num_edges == expected_num_edges


def test_expected_num_edges_with_jobs_example(example_job_shop_instance):
    graph = build_resource_task_graph_with_jobs(example_job_shop_instance)
    expected_num_edges = get_expected_num_edges_for_graph_with_jobs(
        example_job_shop_instance
    )
    assert graph.num_edges == expected_num_edges


def test_expected_num_edges_example(example_job_shop_instance):
    graph = build_resource_task_graph(example_job_shop_instance)
    expected_num_edges = get_expected_num_edges(example_job_shop_instance)
    assert graph.num_edges == expected_num_edges


def test_expected_num_edges_with_jobs():
    benchmark_instances = load_all_benchmark_instances()
    for instance in list(benchmark_instances.values())[:10]:
        graph = build_resource_task_graph_with_jobs(instance)
        expected_num_edges = get_expected_num_edges_for_graph_with_jobs(
            instance
        )
        assert graph.num_edges == expected_num_edges


def test_expected_num_edges():
    benchmark_instances = load_all_benchmark_instances()
    for instance in list(benchmark_instances.values())[:10]:
        graph = build_resource_task_graph(instance)
        expected_num_edges = get_expected_num_edges(instance)
        assert graph.num_edges == expected_num_edges


def get_expected_num_edges_for_complete_graph(
    instance: JobShopInstance,
) -> int:
    num_machine_operation_edges = instance.num_operations
    num_job_operation_edges = instance.num_operations
    num_global_edges = instance.num_jobs + instance.num_machines

    return (
        num_machine_operation_edges
        + num_job_operation_edges
        + num_global_edges
    ) * 2


def get_expected_num_edges_for_graph_with_jobs(
    instance: JobShopInstance,
) -> int:
    num_machine_operation_edges = instance.num_operations
    num_job_operation_edges = instance.num_operations
    # The number of edges of a clique of size n is n * (n - 1) / 2
    num_machine_machine_edges = (
        instance.num_machines * (instance.num_machines - 1) // 2
    )
    num_job_job_edges = instance.num_jobs * (instance.num_jobs - 1) // 2

    return (
        num_machine_operation_edges
        + num_job_operation_edges
        + num_machine_machine_edges
        + num_job_job_edges
    ) * 2


def get_expected_num_edges(instance: JobShopInstance) -> int:
    num_machine_operation_edges = instance.num_operations
    num_machine_machine_edges = (
        instance.num_machines * (instance.num_machines - 1) // 2
    )
    num_same_job_edges = num_machine_machine_edges * instance.num_jobs

    return (
        num_machine_operation_edges
        + num_machine_machine_edges
        + num_same_job_edges
    ) * 2


def get_expected_num_nodes_for_complete_graph(
    instance: JobShopInstance,
) -> int:
    return (
        instance.num_operations + instance.num_jobs + instance.num_machines + 1
    )


def get_expected_num_nodes_for_graph_with_jobs(
    instance: JobShopInstance,
) -> int:
    return instance.num_operations + instance.num_jobs + instance.num_machines


def get_expected_num_nodes(instance: JobShopInstance) -> int:
    return instance.num_operations + instance.num_machines
