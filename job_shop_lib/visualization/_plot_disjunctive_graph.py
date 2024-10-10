"""Module for visualizing the disjunctive graph of a job shop instance."""

import functools
from typing import Optional, Callable
import warnings
import copy

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

from job_shop_lib import JobShopInstance
from job_shop_lib.graphs import (
    JobShopGraph,
    EdgeType,
    NodeType,
    Node,
    build_disjunctive_graph,
)


Layout = Callable[[nx.Graph], dict[str, tuple[float, float]]]


# This function could be improved by a function extraction refactoring
# (see `plot_gantt_chart`
# function as a reference in how to do it). That would solve the
# "too many locals" warning. However, this refactoring is not a priority at
# the moment. To compensate, sections are separated by comments.
# For the "too many arguments" warning no satisfactory solution was
# found. I believe is still better than using `**kwargs` and losing the
# function signature or adding a dataclass for configuration (it would add
# unnecessary complexity). A TypedDict could be used too, but the default
# values would not be explicit.
# pylint: disable=too-many-arguments, too-many-locals
def plot_disjunctive_graph(
    job_shop: JobShopGraph | JobShopInstance,
    *,
    figsize: tuple[float, float] = (6, 4),
    node_size: int = 1600,
    title: Optional[str] = None,
    layout: Optional[Layout] = None,
    edge_width: int = 2,
    font_size: int = 10,
    arrow_size: int = 35,
    alpha=0.95,
    node_font_color: str = "white",
    color_map: str = "Dark2_r",
    draw_disjunctive_edges: bool = True,
    conjunctive_patch_label: str = "Conjunctive edges",
    disjunctive_patch_label: str = "Disjunctive edges",
    legend_text: str = "m = machine_id\nd = duration",
) -> plt.Figure:
    """Plots the disjunctive graph of the given job shop instance or graph.

    Args:
        job_shop:
            The job shop instance or graph to plot. Can be either a
            :class:`JobShopGraph` or a :class:`JobShopInstance`.
        figsize:
            The size of the figure (default is (6, 4)).
        node_size:
            The size of the nodes (default is 1600).
        title:
            The title of the graph (default is ``None``).
        layout:
            The layout of the graph (default is ``None``).
        edge_width:
            The width of the edges (default is 2).
        font_size:
            The font size of the node labels (default is 10).
        arrow_size:
            The size of the arrows (default is 35).
        alpha:
            The transparency level of the nodes and edges (default is 0.95).
        node_font_color:
            The color of the node labels (default is ``"white"``).
        color_map:
            The color map to use for the nodes (default is ``"Dark2_r"``).
        draw_disjunctive_edges:
            Whether to draw disjunctive edges (default is ``True``).
        conjunctive_patch_label:
            The label for the conjunctive edges in the legend (default is
            "Conjunctive edges").
        disjunctive_patch_label:
            The label for the disjunctive edges in the legend (default is
            "Disjunctive edges").
        legend_text:
            The text to display in the legend after the conjunctive and
            disjunctive edges labels (default is
            ``"m = machine_id\nd = duration"``).

    Returns:
        A matplotlib Figure object representing the disjunctive graph.

    Example:
        >>> job_shop_instance = JobShopInstance(...)
        >>> fig = plot_disjunctive_graph(job_shop_instance)
        >>> fig.show()
    """

    if isinstance(job_shop, JobShopInstance):
        job_shop_graph = build_disjunctive_graph(job_shop)
    else:
        job_shop_graph = job_shop

    # Set up the plot
    # ----------------
    plt.figure(figsize=figsize)
    if title is None:
        title = (
            f"Disjunctive Graph Visualization: {job_shop_graph.instance.name}"
        )
    plt.title(title)

    # Set up the layout
    # -----------------
    if layout is None:
        layout = functools.partial(
            graphviz_layout, prog="dot", args="-Grankdir=LR"
        )

    temp_graph = copy.deepcopy(job_shop_graph.graph)
    # Remove disjunctive edges to get a better layout
    temp_graph.remove_edges_from(
        [
            (u, v)
            for u, v, d in job_shop_graph.graph.edges(data=True)
            if d["type"] == EdgeType.DISJUNCTIVE
        ]
    )

    try:
        pos = layout(temp_graph)
    except ImportError:
        warnings.warn(
            "Default layout requires pygraphviz http://pygraphviz.github.io/. "
            "Using spring layout instead.",
        )
        pos = nx.spring_layout(temp_graph)

    # Draw nodes
    # ----------
    node_colors = [
        _get_node_color(node)
        for node in job_shop_graph.nodes
        if not job_shop_graph.is_removed(node.node_id)
    ]

    nx.draw_networkx_nodes(
        job_shop_graph.graph,
        pos,
        node_size=node_size,
        node_color=node_colors,
        alpha=alpha,
        cmap=matplotlib.colormaps.get_cmap(color_map),
    )

    # Draw edges
    # ----------
    conjunctive_edges = [
        (u, v)
        for u, v, d in job_shop_graph.graph.edges(data=True)
        if d["type"] == EdgeType.CONJUNCTIVE
    ]
    disjunctive_edges = [
        (u, v)
        for u, v, d in job_shop_graph.graph.edges(data=True)
        if d["type"] == EdgeType.DISJUNCTIVE
    ]

    nx.draw_networkx_edges(
        job_shop_graph.graph,
        pos,
        edgelist=conjunctive_edges,
        width=edge_width,
        edge_color="black",
        arrowsize=arrow_size,
    )

    if draw_disjunctive_edges:
        nx.draw_networkx_edges(
            job_shop_graph.graph,
            pos,
            edgelist=disjunctive_edges,
            width=edge_width,
            edge_color="red",
            arrowsize=arrow_size,
        )

    # Draw node labels
    # ----------------
    operation_nodes = job_shop_graph.nodes_by_type[NodeType.OPERATION]

    labels = {}
    source_node = job_shop_graph.nodes_by_type[NodeType.SOURCE][0]
    labels[source_node] = "S"

    sink_node = job_shop_graph.nodes_by_type[NodeType.SINK][0]
    labels[sink_node] = "T"
    for operation_node in operation_nodes:
        if job_shop_graph.is_removed(operation_node.node_id):
            continue
        labels[operation_node] = (
            f"m={operation_node.operation.machine_id}\n"
            f"d={operation_node.operation.duration}"
        )

    nx.draw_networkx_labels(
        job_shop_graph.graph,
        pos,
        labels=labels,
        font_color=node_font_color,
        font_size=font_size,
        font_family="sans-serif",
    )

    # Final touches
    # -------------
    plt.axis("off")
    plt.tight_layout()
    # Create a legend to indicate the meaning of the edge colors
    conjunctive_patch = matplotlib.patches.Patch(
        color="black", label=conjunctive_patch_label
    )
    disjunctive_patch = matplotlib.patches.Patch(
        color="red", label=disjunctive_patch_label
    )

    # Add to the legend the meaning of m and d
    extra = matplotlib.patches.Rectangle(
        (0, 0),
        1,
        1,
        fc="w",
        fill=False,
        edgecolor="none",
        linewidth=0,
        label=legend_text,
    )
    plt.legend(
        handles=[conjunctive_patch, disjunctive_patch, extra],
        loc="upper left",
        bbox_to_anchor=(1.05, 1),
        borderaxespad=0.0,
    )
    return plt.gcf()


def _get_node_color(node: Node) -> int:
    """Returns the color of the node."""
    if node.node_type == NodeType.SOURCE:
        return -1
    if node.node_type == NodeType.SINK:
        return -1
    if node.node_type == NodeType.OPERATION:
        return node.operation.machine_id

    raise ValueError("Invalid node type.")
