from job_shop_lib import JobShopInstance
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.rules import DispatchingRuleSolver
from job_shop_lib.dispatching.feature_observers import (
    IsCompletedObserver,
    FeatureType,
)
from job_shop_lib.graphs import (
    build_disjunctive_graph,
    build_resource_task_graph,
    JobShopGraph,
    NodeType,
)
from job_shop_lib.graphs.graph_updaters import ResidualGraphUpdater


def _verify_all_nodes_removed(job_shop_graph: JobShopGraph):
    for node in job_shop_graph.nodes:
        assert job_shop_graph.is_removed(
            node.node_id
        ), f"Node {node.node_id} was not removed."


def test_removes_all_nodes_disjunctive_graph(
    example_job_shop_instance: JobShopInstance,
):

    job_shop_graph = build_disjunctive_graph(example_job_shop_instance)

    # Remove source and sink nodes
    source_node = job_shop_graph.nodes_by_type[NodeType.SOURCE][0]
    sink_node = job_shop_graph.nodes_by_type[NodeType.SINK][0]
    job_shop_graph.remove_node(source_node.node_id)
    job_shop_graph.remove_node(sink_node.node_id)
    dispatcher = Dispatcher(example_job_shop_instance)

    # Initialize ResidualGraphUpdater
    ResidualGraphUpdater(
        dispatcher,
        job_shop_graph,
        subscribe=True,
        remove_completed_job_nodes=True,
        remove_completed_machine_nodes=True,
    )

    # Initialize the DispatchingRuleSolver with the most work remaining rule
    solver = DispatchingRuleSolver(dispatching_rule="most_work_remaining")

    # Solve the job shop instance to simulate completing all operations
    solver.solve(dispatcher.instance, dispatcher)

    _verify_all_nodes_removed(job_shop_graph)


def test_removes_all_nodes_agent_task_graph():
    instance_dict = {
        "name": "classic_generated_instance_2",
        "duration_matrix": [
            [59, 91, 94, 56, 69],
            [11, 34, 85, 27, 30],
            [99, 23, 25, 48, 27],
            [60, 36, 21, 82, 24],
        ],
        "machines_matrix": [
            [1, 4, 2, 0, 3],
            [3, 0, 4, 2, 1],
            [1, 2, 3, 4, 0],
            [4, 3, 2, 0, 1],
        ],
        "metadata": {},
    }
    instance = JobShopInstance.from_matrices(
        **instance_dict  # type: ignore[arg-type]
    )
    job_shop_graph = build_resource_task_graph(instance)
    dispatcher = Dispatcher(instance)

    # Initialize ResidualGraphUpdater
    ResidualGraphUpdater(
        dispatcher,
        job_shop_graph,
        subscribe=True,
        remove_completed_job_nodes=True,
        remove_completed_machine_nodes=True,
    )

    # Initialize the DispatchingRuleSolver with the most work remaining rule
    solver = DispatchingRuleSolver(dispatching_rule="most_work_remaining")

    # Solve the job shop instance to simulate completing all operations
    solver.solve(dispatcher.instance, dispatcher)

    _verify_all_nodes_removed(job_shop_graph)


def test_initialization(example_job_shop_instance: JobShopInstance):
    job_shop_graph = build_resource_task_graph(example_job_shop_instance)
    dispatcher = Dispatcher(example_job_shop_instance)

    # Initialize ResidualGraphUpdater
    updater = ResidualGraphUpdater(
        dispatcher,
        job_shop_graph,
        subscribe=True,
        remove_completed_job_nodes=True,
        remove_completed_machine_nodes=True,
    )

    assert updater.job_shop_graph == job_shop_graph
    assert updater.dispatcher is dispatcher
    assert updater.remove_completed_job_nodes
    assert updater.remove_completed_machine_nodes
    assert isinstance(updater.is_completed_observer, IsCompletedObserver)
    assert set(updater.is_completed_observer.features) == {
        FeatureType.MACHINES,
        FeatureType.JOBS,
    }


if __name__ == "__main__":
    import pytest

    pytest.main(["-vv", "tests/graphs/test_residual_graph_updater.py"])
