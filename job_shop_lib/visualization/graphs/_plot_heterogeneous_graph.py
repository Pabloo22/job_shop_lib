"""Contains functions to plot a resource-task graph representation of a job
shop instance.

It was introduced by Junyoung Park et al. (2021).
In contrast to the disjunctive graph, instead of connecting operations that
share the same resources directly by disjunctive edges, operation nodes are
connected with machine ones. All machine nodes are connected between them, and
all operation nodes from the same job are connected by non-directed edges too.
"""

from collections.abc import Callable
from copy import deepcopy
from typing import Optional, Any, Tuple, Dict, Union, List

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx

from job_shop_lib.graphs import NodeType, JobShopGraph, Node


def plot_resource_task_graph(
    job_shop_graph: JobShopGraph,
    *,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 10),
    layout: Optional[Dict[Node, Tuple[float, float]]] = None,
    node_size: int = 1200,
    node_font_color: str = "k",
    font_size: int = 10,
    alpha: float = 0.95,
    add_legend: bool = False,
    node_shapes: Optional[Dict[str, str]] = None,
    node_color_map: Optional[
        Callable[[Node], Tuple[float, float, float, float]]
    ] = None,
    default_node_color: Union[
        str, Tuple[float, float, float, float]
    ] = "lightblue",
    machine_color_map_name: str = "tab10",
    legend_text: str = "$p_{ij}$ = duration of $O_{ij}$",
    edge_additional_params: Optional[Dict[str, Any]] = None,
    draw_only_one_edge: bool = False,
) -> plt.Figure:
    """Returns a plot of the hetereogeneous graph of the instance.

    Machine and job nodes are represented by squares, and the operation nodes
    are represented by circles.

    Args:
        job_shop_graph:
            The job shop graph instance.
        title:
            The title of the plot. If ``None``, the title "Heterogeneous Graph
            Visualization: {instance_name}" is used. The default is ``None``.
        figsize:
            The size of the figure. It should be a tuple with the width and
            height in inches. The default is ``(10, 10)``.
        layout:
            A dictionary with the position of each node in the graph. The keys
            are the node ids, and the values are tuples with the x and y
            coordinates. If ``None``, the :func:`three_columns_layout` function
            is used. The default is ``None``.
        node_size:
            The size of the nodes. The default is 1000.
        alpha:
            The transparency of the nodes. It should be a float between 0 and
            1. The default is 0.95.
        add_legend:
            Whether to add a legend with the meaning of the colors and shapes.
            The default is ``False``.
        node_shapes:
            A dictionary with the shapes of the nodes. The keys are the node
            types, and the values are the shapes. The default is
            ``{"machine": "s", "job": "d", "operation": "o", "global": "o"}``.
        node_color_map:
            A function that receives a node and returns a tuple with the RGBA
            values of the color to use in the plot. If ``None``,
            :func:`color_nodes_by_machine` is used.
        machine_color_map_name:
            The name of the colormap to use for the machines. This argument is
            only used if ``node_color_map`` is ``None``. The default is
            ``"tab10"``.

    Returns:
        The figure of the plot. This figure can be used to save the plot to a
        file or to show it in a Jupyter notebook.
    """
    if title is None:
        title = (
            "Heterogeneous Graph Visualization:"
            f"{job_shop_graph.instance.name}"
        )
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle(title)

    # Create the networkx graph
    graph = job_shop_graph.graph
    nodes = job_shop_graph.non_removed_nodes()

    # Create the layout if it was not provided
    if layout is None:
        layout = three_columns_layout(job_shop_graph)

    # Define colors and shapes
    color_map = plt.get_cmap(machine_color_map_name)
    machine_colors = {
        machine.machine_id: color_map(i)
        for i, machine in enumerate(
            job_shop_graph.nodes_by_type[NodeType.MACHINE]
        )
    }
    node_color_map = (
        color_nodes_by_machine(machine_colors, default_node_color)
        if node_color_map is None
        else node_color_map
    )
    node_colors = [
        node_color_map(node) for node in job_shop_graph.nodes
    ]  # We need to get the color of all nodes to avoid an index error
    if node_shapes is None:
        node_shapes = {
            "machine": "s",
            "job": "d",
            "operation": "o",
            "global": "o",
        }

    # Draw nodes with different shapes based on their type
    for node_type, shape in node_shapes.items():
        current_nodes = [
            node.node_id
            for node in nodes
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
    if edge_additional_params is None:
        edge_additional_params = {}
    if draw_only_one_edge:
        graph = deepcopy(graph)
        edges = list(graph.edges)
        present_edges = set()
        for edge in edges:
            unorder_edge = frozenset(edge)
            if unorder_edge in present_edges:
                graph.remove_edge(*edge)
            else:
                present_edges.add(unorder_edge)

    nx.draw_networkx_edges(graph, layout, ax=ax, **edge_additional_params)

    node_color_map = (
        color_nodes_by_machine(machine_colors, "lightblue")
        if node_color_map is None
        else node_color_map
    )
    node_labels = {node.node_id: _get_node_label(node) for node in nodes}
    nx.draw_networkx_labels(
        graph,
        layout,
        node_labels,
        ax=ax,
        font_size=font_size,
        font_color=node_font_color,
    )

    ax.set_axis_off()

    plt.tight_layout()

    # Add to the legend the meaning of m and d
    if add_legend:
        plt.figtext(0, 0.95, legend_text, wrap=True, fontsize=12)
    return fig


def _get_node_label(node: Node) -> str:
    if node.node_type == NodeType.OPERATION:
        i = node.operation.job_id
        j = node.operation.position_in_job
        ij = str(i) + str(j)
        return f"$p_{{{ij}}}={node.operation.duration}$"
    if node.node_type == NodeType.MACHINE:
        return f"$M_{node.machine_id}$"
    if node.node_type == NodeType.JOB:
        return f"$J_{node.job_id}$"
    if node.node_type == NodeType.GLOBAL:
        return "$G$"

    raise ValueError(f"Invalid node type: {node.node_type}")


def _color_to_rgba(
    color: Union[str, Tuple[float, float, float, float]]
) -> Tuple[float, float, float, float]:
    if isinstance(color, str):
        return mcolors.to_rgba(color)
    return color


def color_nodes_by_machine(
    machine_colors: Dict[int, Tuple[float, float, float, float]],
    default_color: Union[str, Tuple[float, float, float, float]],
) -> Callable[[Node], Tuple[float, float, float, float]]:
    """Returns a function that assigns a color to a node based on its type.

    The function returns a color based on the node type. If the node is an
    operation, the color is based on the machine it is assigned to. If the node
    is a machine, the color is based on the machine id. If the node is a job or
    global node, the color is the default color.

    Args:
        machine_colors:
            A dictionary with the colors of each machine. The keys are the
            machine ids, and the values are tuples with the RGBA values.
        default_color:
            The default color to use for job and global nodes. It can be a
            string with a color name or a tuple with the RGBA values.

    Returns:
        A function that receives a node and returns a tuple with the RGBA
        values of the color to use in the plot.
    """

    def _get_node_color(node: Node) -> Tuple[float, float, float, float]:
        if node.node_type == NodeType.OPERATION:
            return machine_colors[node.operation.machine_id]
        if node.node_type == NodeType.MACHINE:
            return machine_colors[node.machine_id]

        return _color_to_rgba(default_color)

    return _get_node_color


def three_columns_layout(
    job_shop_graph: JobShopGraph,
    *,
    leftmost_position: float = 0.1,
    rightmost_position: float = 0.9,
    topmost_position: float = 1.0,
    bottommost_position: float = 0.0,
) -> Dict[Node, Tuple[float, float]]:
    """Generates coordinates for a three-column grid layout.

    1. Left column: Machine nodes (M1, M2, etc.)
    2. Middle column: Operation nodes (O_ij where i=job, j=operation)
    3. Right column: Job nodes (J1, J2, etc.)

    The operations are arranged vertically in groups by job, with a global
    node (G) at the bottom.

    For example, in a 2-machine, 3-job problem:

    - Machine nodes (M1, M2) appear in the left column where needed
    - Operation nodes (O_11 through O_33) form the central column
    - Job nodes (J1, J2, J3) appear in the right column at the middle of their
      respective operations
    - The global node (G) appears at the bottom of the middle column

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

    operation_nodes = [
        node
        for node in job_shop_graph.nodes_by_type[NodeType.OPERATION]
        if not job_shop_graph.is_removed(node)
    ]
    machine_nodes = [
        node
        for node in job_shop_graph.nodes_by_type[NodeType.MACHINE]
        if not job_shop_graph.is_removed(node)
    ]
    job_nodes = [
        node
        for node in job_shop_graph.nodes_by_type[NodeType.JOB]
        if not job_shop_graph.is_removed(node)
    ]
    global_nodes = [
        node
        for node in job_shop_graph.nodes_by_type[NodeType.GLOBAL]
        if not job_shop_graph.is_removed(node)
    ]

    # job_nodes = job_shop_graph.nodes_by_type[NodeType.JOB]
    # global_nodes = job_shop_graph.nodes_by_type[NodeType.GLOBAL]

    total_positions = len(operation_nodes) + len(global_nodes) * 2
    y_spacing = (topmost_position - bottommost_position) / total_positions

    layout: Dict[Node, Tuple[float, float]] = {}

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
) -> Dict[str, float]:
    center_position = (
        leftmost_position + (rightmost_position - leftmost_position) / 2
    )
    return {
        "machine": leftmost_position,
        "operation": center_position,
        "job": rightmost_position,
    }


def _assign_positions_from_top(
    nodes: List[Node],
    x: float,
    top: float,
    y_spacing: float,
) -> Dict[Node, Tuple[float, float]]:
    layout: Dict[Node, Tuple[float, float]] = {}
    for i, node in enumerate(nodes):
        y = top - (i + 1) * y_spacing
        layout[node] = (x, y)

    return layout
