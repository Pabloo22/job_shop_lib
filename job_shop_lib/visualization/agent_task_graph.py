"""Contains functions to plot the agent-task graph of a job shop instance.

The agent-task graph was introduced by Junyoung Park et al. (2021).
In contrast to the disjunctive graph, instead of connecting operations that
share the same resources directly by disjunctive edges, operation nodes are
connected with machine ones. All machine nodes are connected between them, and
all operation nodes from the same job are connected by non-directed edges too.

See: job_shop_lib.graphs.build_agent_task_graph module for more information.
"""

from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx

from job_shop_lib.graphs import NodeType, JobShopGraph, Node


def plot_agent_task_graph(
    job_shop_graph: JobShopGraph,
    title: Optional[str] = None,
    figsize: tuple[int, int] = (10, 10),
    layout: Optional[dict[Node, tuple[float, float]]] = None,
    color_map_name: str = "tab10",
    node_size: int = 1000,
    alpha: float = 0.95,
    add_legend: bool = False,
) -> plt.Figure:
    """Returns a plot of the agent-task graph of the instance.

    Machine and job nodes are represented by squares, and the operation nodes
    are represented by circles.

    Args:
        job_shop_graph:
            The job shop graph instance. It should be already initialized with
            the instance with a valid agent-task graph representation.

    Returns:
        The figure of the plot. This figure can be used to save the plot to a
        file or to show it in a Jupyter notebook.
    """
    if title is None:
        title = (
            f"Agent-Task Graph Visualization: {job_shop_graph.instance.name}"
        )
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle(title)

    # Create the networkx graph
    graph = job_shop_graph.graph

    # Create the layout if it was not provided
    if layout is None:
        layout = three_columns_layout(job_shop_graph)

    # Define colors and shapes
    color_map = plt.get_cmap(color_map_name)
    machine_colors = {
        machine.machine_id: color_map(i)
        for i, machine in enumerate(
            job_shop_graph.nodes_by_type[NodeType.MACHINE]
        )
    }
    node_colors = [
        _get_node_color(node, machine_colors) for node in job_shop_graph.nodes
    ]
    node_shapes = {"machine": "s", "job": "d", "operation": "o", "global": "o"}

    # Draw nodes with different shapes based on their type
    for node_type, shape in node_shapes.items():
        current_nodes = [
            node.node_id
            for node in job_shop_graph.nodes
            if node.node_type.name.lower() == node_type
        ]
        nx.draw_networkx_nodes(
            graph,
            layout,
            nodelist=current_nodes,
            node_color=[node_colors[i] for i in current_nodes],
            node_shape=shape,
            ax=ax,
            node_size=node_size,
            alpha=alpha,
        )

    # Draw edges
    nx.draw_networkx_edges(graph, layout, ax=ax)

    node_labels = {
        node.node_id: _get_node_label(node) for node in job_shop_graph.nodes
    }
    nx.draw_networkx_labels(graph, layout, node_labels, ax=ax)

    ax.set_axis_off()

    plt.tight_layout()

    # Add to the legend the meaning of m and d
    if add_legend:
        plt.figtext(0, 0.95, "d = duration", wrap=True, fontsize=12)
    return fig


def _get_node_color(
    node: Node, machine_colors: dict[int, tuple[float, float, float, float]]
) -> tuple[float, float, float, float] | str:
    if node.node_type == NodeType.OPERATION:
        return machine_colors[node.operation.machine_id]
    if node.node_type == NodeType.MACHINE:
        return machine_colors[node.machine_id]

    return "lightblue"


def _get_node_label(node: Node) -> str:
    if node.node_type == NodeType.OPERATION:
        return f"d={node.operation.duration}"
    if node.node_type == NodeType.MACHINE:
        return f"M{node.machine_id}"
    if node.node_type == NodeType.JOB:
        return f"J{node.job_id}"
    if node.node_type == NodeType.GLOBAL:
        return "G"

    raise ValueError(f"Invalid node type: {node.node_type}")


def three_columns_layout(
    job_shop_graph: JobShopGraph,
    *,
    leftmost_position: float = 0.1,
    rightmost_position: float = 0.9,
    topmost_position: float = 1.0,
    bottommost_position: float = 0.0,
) -> dict[Node, tuple[float, float]]:
    """Returns the layout of the agent-task graph.

    The layout is organized in a grid manner. For example, for a JobShopGraph
    representing a job shop instance with 2 machines and 3 jobs, the layout
    would be:

    0:  -       O_11      -
    1:  -       O_12      J1
    2:  -       O_13      -
    3:  M1      O_21      -
    4:  -       O_22      J2
    5:  -       O_23      -
    6:  M2      O_31      -
    7:  -       O_32      J3
    8:  -       O_33      -
    9:  -        -        -
    10: -        G        -
    Where M1 and M2 are the machine nodes, J1, J2, and J3 are the job
    nodes, O_ij are the operation nodes, and G is the global node.

    Args:
        job_shop_graph:
            The job shop graph instance. It should be already initialized with
            the instance with a valid agent-task graph representation.
        leftmost_position:
            The center position of the leftmost column of the layout. It should
            be a float between 0 and 1. The default is 0.1.
        rightmost_position:
            The center position of the rightmost column of the layout. It
            should be a float between 0 and 1. The default is 0.9.
        topmost_position:
            The center position of the topmost node of the layout. It should be
            a float between 0 and 1. The default is 0.9.
        bottommost_position:
            The center position of the bottommost node of the layout. It should
            be a float between 0 and 1. The default is 0.1.

    Returns:
        A dictionary with the position of each node in the graph. The keys are
        the node ids, and the values are tuples with the x and y coordinates.
    """

    x_positions = _get_x_positions(leftmost_position, rightmost_position)

    operation_nodes = job_shop_graph.nodes_by_type[NodeType.OPERATION]
    machine_nodes = job_shop_graph.nodes_by_type[NodeType.MACHINE]
    job_nodes = job_shop_graph.nodes_by_type[NodeType.JOB]
    global_nodes = job_shop_graph.nodes_by_type[NodeType.GLOBAL]

    total_positions = len(operation_nodes) + len(global_nodes) * 2
    y_spacing = (topmost_position - bottommost_position) / total_positions

    layout: dict[Node, tuple[float, float]] = {}

    machines_spacing_multiplier = len(operation_nodes) // len(machine_nodes)
    layout.update(
        _assign_positions_from_top(
            machine_nodes,
            x_positions["machine"],
            topmost_position,
            y_spacing * machines_spacing_multiplier,
        )
    )
    layout.update(
        (
            _assign_positions_from_top(
                operation_nodes,
                x_positions["operation"],
                topmost_position,
                y_spacing,
            )
        )
    )

    if global_nodes:
        layout[global_nodes[0]] = (
            x_positions["operation"],
            bottommost_position,
        )

    if job_nodes:
        job_multiplier = len(operation_nodes) // len(job_nodes)
        layout.update(
            _assign_positions_from_top(
                job_nodes,
                x_positions["job"],
                topmost_position,
                y_spacing * job_multiplier,
            )
        )
    return layout


def _get_x_positions(
    leftmost_position: float, rightmost_position: float
) -> dict[str, float]:
    center_position = (
        leftmost_position + (rightmost_position - leftmost_position) / 2
    )
    return {
        "machine": leftmost_position,
        "operation": center_position,
        "job": rightmost_position,
    }


def _assign_positions_from_top(
    nodes: list[Node],
    x: float,
    top: float,
    y_spacing: float,
) -> dict[Node, tuple[float, float]]:
    layout: dict[Node, tuple[float, float]] = {}
    for i, node in enumerate(nodes):
        y = top - (i + 1) * y_spacing
        layout[node] = (x, y)

    return layout
