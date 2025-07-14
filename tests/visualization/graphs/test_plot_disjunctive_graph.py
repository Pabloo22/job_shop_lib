import warnings

import pytest
import matplotlib

from job_shop_lib import JobShopInstance
from job_shop_lib.graphs import build_disjunctive_graph, NodeType, Node
from job_shop_lib.visualization.graphs import plot_disjunctive_graph
from job_shop_lib.exceptions import ValidationError


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_default_plot_disjunctive_graph(
    example_job_shop_instance: JobShopInstance,
):
    graph = build_disjunctive_graph(example_job_shop_instance)

    fig, _ = plot_disjunctive_graph(graph)
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_disjunctive_graph_single_edge_machine_colors(
    example_job_shop_instance: JobShopInstance,
):
    """
    Tests plot_disjunctive_graph with specific machine_colors and
    draw_disjunctive_edges="single_edge".
    """
    graph = build_disjunctive_graph(example_job_shop_instance)

    num_machines = example_job_shop_instance.num_machines
    cmap = matplotlib.colormaps.get_cmap("viridis")
    machine_colors = {
        i: cmap(i / num_machines if num_machines > 0 else 0.5)
        for i in range(num_machines)
    }
    machine_colors[-1] = (0.5, 0.5, 0.5, 1.0)  # Color for source/sink nodes

    machine_labels = [f"Machine {i}" for i in range(num_machines)]

    fig, _ = plot_disjunctive_graph(
        graph,
        title="Test: Single Edge & Machine Colors",
        machine_colors=machine_colors,
        draw_disjunctive_edges="single_edge",
        disjunctive_edges_additional_params={
            "arrowstyle": "<|-|>",
            "connectionstyle": "arc3,rad=0.15",
        },
        machine_labels=machine_labels,
        show_machine_colors_in_legend=True,
    )
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_disjunctive_graph_removed_nodes(
    example_job_shop_instance: JobShopInstance,
):
    """
    Tests plot_disjunctive_graph with a graph where nodes have been removed,
    also using machine_colors and single_edge for disjunctive edges.
    """
    graph = build_disjunctive_graph(example_job_shop_instance)

    op_nodes = [
        node for node in graph.nodes if node.node_type == NodeType.OPERATION
    ]

    # Remove 1st, 3rd, 4th operation nodes if they exist
    nodes_to_remove_indices = [0, 2, 3]
    removed_count = 0
    for index_to_remove in nodes_to_remove_indices:
        actual_index = index_to_remove - removed_count
        if actual_index < len(op_nodes):
            node_to_remove = op_nodes.pop(actual_index)
            if not graph.is_removed(node_to_remove.node_id):
                graph.remove_node(node_to_remove.node_id)
                removed_count += 1

    num_machines = example_job_shop_instance.num_machines
    cmap = matplotlib.colormaps.get_cmap("plasma")
    machine_colors = {
        i: cmap(i / num_machines if num_machines > 0 else 0.5)
        for i in range(num_machines)
    }
    machine_colors[-1] = (0.6, 0.6, 0.6, 1.0)  # Color for source/sink

    machine_labels = [f"M_{i}" for i in range(num_machines)]

    fig, _ = plot_disjunctive_graph(
        graph,
        title="Test: Removed Nodes",
        machine_colors=machine_colors,
        draw_disjunctive_edges="single_edge",
        disjunctive_edges_additional_params={
            "arrowstyle": "<|-|>",
            "connectionstyle": "arc3,rad=0.15",
        },
        machine_labels=machine_labels,
        show_machine_colors_in_legend=True,
    )
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_disjunctive_graph_removed_nodes_default_machine_colors(
    example_job_shop_instance: JobShopInstance,
):
    graph = build_disjunctive_graph(example_job_shop_instance)

    op_nodes = [
        node for node in graph.nodes if node.node_type == NodeType.OPERATION
    ]

    # Remove 1st, 3rd, 4th operation nodes if they exist
    nodes_to_remove_indices = [0, 2, 3]
    removed_count = 0
    for index_to_remove in nodes_to_remove_indices:
        actual_index = index_to_remove - removed_count
        if actual_index < len(op_nodes):
            node_to_remove = op_nodes.pop(actual_index)
            if not graph.is_removed(node_to_remove.node_id):
                graph.remove_node(node_to_remove.node_id)
                removed_count += 1

    num_machines = example_job_shop_instance.num_machines
    machine_labels = [f"M_{i}" for i in range(num_machines)]

    fig, _ = plot_disjunctive_graph(
        graph,
        title="Test: Removed Nodes",
        draw_disjunctive_edges="single_edge",
        disjunctive_edges_additional_params={
            "arrowstyle": "<|-|>",
            "connectionstyle": "arc3,rad=0.15",
        },
        machine_labels=machine_labels,
        show_machine_colors_in_legend=True,
    )
    return fig


def test_graph_with_invalid_node_type(
    example_job_shop_instance: JobShopInstance,
):
    """
    Tests plot_disjunctive_graph with a graph that has an invalid node type.
    """
    graph = build_disjunctive_graph(example_job_shop_instance)

    # Add an invalid node type
    graph.add_node(Node(node_type=NodeType.GLOBAL))

    with pytest.raises(ValidationError):
        plot_disjunctive_graph(graph)


def mock_layout(*args, **kwargs):
    """Simulates that pygraphviz is not installed."""
    raise ImportError


def test_fallback_layout(
    example_job_shop_instance: JobShopInstance,
):
    graph = build_disjunctive_graph(example_job_shop_instance)
    # If pygraphviz is not installed, it should not raise an ImportError
    # but a warning.
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        plot_disjunctive_graph(graph, layout=mock_layout)
        assert any(
            "Default layout requires pygraphviz" in str(warn.message)
            for warn in w
        )


if __name__ == "__main__":
    pytest.main(
        ["-v", __file__, "--mpl-generate-path=tests/visualization/baseline"]
    )
