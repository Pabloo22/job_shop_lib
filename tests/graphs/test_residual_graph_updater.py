from job_shop_lib import JobShopInstance
from job_shop_lib.dispatching import Dispatcher, DispatchingRuleSolver
from job_shop_lib.graphs import build_disjunctive_graph
from job_shop_lib.graphs.graph_updaters import ResidualGraphUpdater


def test_residual_graph_updater_removes_all_nodes(
    example_job_shop_instance: JobShopInstance,
):

    job_shop_graph = build_disjunctive_graph(example_job_shop_instance)
    dispatcher = Dispatcher(example_job_shop_instance)

    # Initialize ResidualGraphUpdater
    ResidualGraphUpdater(
        dispatcher,
        job_shop_graph,
        is_singleton=False,
        subscribe=True,
        remove_completed_job_nodes=True,
        remove_completed_machine_nodes=True,
    )

    # Initialize the DispatchingRuleSolver with the most work remaining rule
    solver = DispatchingRuleSolver(dispatching_rule="most_work_remaining")

    # Solve the job shop instance to simulate completing all operations
    solver.solve(dispatcher.instance, dispatcher)

    # Verify all nodes are removed
    for node in job_shop_graph.nodes:
        assert job_shop_graph.is_removed(
            node.node_id
        ), f"Node {node.node_id} was not removed."


if __name__ == "__main__":
    import pytest

    pytest.main(["-vv", "tests/graphs/test_residual_graph_updater.py"])
