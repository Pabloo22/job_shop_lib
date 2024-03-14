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

from job_shop_lib.graphs import NodeType, JobShopGraph, Node, NODE_ATTR


def plot_agent_task_graph(
    job_shop_graph: JobShopGraph,
    figsize: tuple[int, int] = (10, 10),
    layout: Optional[dict[Node, tuple[float, float]]] = None,
    color_map_name: str = "tab10",
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
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=figsize)

    # Create the networkx graph
    graph = job_shop_graph.graph

    # Create the layout if it was not provided
    if layout is None:
        layout = task_agent_layout(job_shop_graph)

    # Define colors and shapes
    color_map = plt.get_cmap(color_map_name)
    machine_colors = {
        machine.node_id: color_map(i)
        for i, machine in enumerate(
            job_shop_graph.nodes_by_type[NodeType.MACHINE]
        )
    }
    node_colors = [
        (
            machine_colors.get(node.operation.machine_id, "gray")
            if node.node_type == NodeType.OPERATION
            else "lightblue"
        )
        for node in job_shop_graph.nodes
    ]
    node_shapes = {"machine": "s", "job": "s", "operation": "o", "global": "o"}

    # Draw nodes with different shapes based on their type
    for node_type, shape in node_shapes.items():
        nx.draw_networkx_nodes(
            graph,
            layout,
            nodelist=job_shop_graph.nodes,
            node_color=[
                node_colors[node.node_id]
                for node in graph.nodes(data=NODE_ATTR)
                if node.node_type.name.lower() == node_type
            ],
            node_shape=shape,
            ax=ax,
        )

    # Draw edges
    nx.draw_networkx_edges(graph, layout, ax=ax)

    # Draw labels
    labels = {node.node_id: str(node.node_id) for node in job_shop_graph.nodes}
    nx.draw_networkx_labels(graph, layout, labels, ax=ax)

    ax.set_axis_off()
    return fig


def task_agent_layout(
    job_shop_graph: JobShopGraph,
    *,
    leftmost_position: float = 0.1,
    rightmost_position: float = 0.9,
    topmost_position: float = 0.9,
    bottommost_position: float = 0.1,
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
    center_position = (
        leftmost_position + (rightmost_position - leftmost_position) / 2
    )
    x_positions = {
        "machine": leftmost_position,
        "operation": center_position,
        "job": rightmost_position,
    }

    operation_nodes = job_shop_graph.nodes_by_type[NodeType.OPERATION]
    machine_nodes = job_shop_graph.nodes_by_type[NodeType.MACHINE]
    job_nodes = job_shop_graph.nodes_by_type[NodeType.JOB]
    global_nodes = job_shop_graph.nodes_by_type[NodeType.GLOBAL]

    total_positions = len(operation_nodes) + len(global_nodes) * 2
    y_spacing = (topmost_position - bottommost_position) / total_positions

    layout: dict[Node, tuple[float, float]] = {}

    _assign_positions_from_top(
        layout,
        machine_nodes,
        x_positions["machine"],
        topmost_position,
        y_spacing,
    )
    _assign_positions_from_top(
        layout,
        operation_nodes,
        x_positions["operation"],
        topmost_position,
        y_spacing,
    )

    if global_nodes:
        global_node = global_nodes[0]
        layout[global_node] = (x_positions["operation"], bottommost_position)

    _assign_positions_from_top(
        layout, job_nodes, x_positions["job"], topmost_position, y_spacing
    )
    return layout


def _assign_positions_from_top(
    layout: dict[Node, tuple[float, float]],
    nodes: list[Node],
    x: float,
    top: float,
    y_spacing: float,
) -> None:
    for i, node in enumerate(nodes):
        y = top - (i + 1) * y_spacing
        layout[node] = (x, y)
