"""Module for visualizing the disjunctive graph of a job shop instance."""

import functools
from typing import Any
from collections.abc import Callable, Sequence, Iterable
import warnings
import copy

import matplotlib
import matplotlib.colors
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
from job_shop_lib.exceptions import ValidationError


Layout = Callable[[nx.Graph], dict[str, tuple[float, float]]]


def duration_labeler(node: Node) -> str:
    """Returns a label for the node with the processing time.

    In the form ``"$p_{ij}=duration$"``, where $i$ is the job id and $j$ is
    the position in the job.

    Args:
        node:
            The operation node to label. See
            :class:`~job_shop_lib.graphs.Node`.
    """
    return (
        f"$p_{{{node.operation.job_id + 1}"
        f"{node.operation.position_in_job + 1}}}={node.operation.duration}$"
    )


# This function could be improved by a function extraction refactoring
# (see `plot_gantt_chart`
# function as a reference in how to do it). That would solve the
# "too many locals" warning. However, this refactoring is not a priority at
# the moment. To compensate, sections are separated by comments.
# For the "too many arguments" warning no satisfactory solution was
# found. I believe is still better than using `**kwargs` and losing the
# function signature or adding a dataclass for configuration (it would add
# more complexity). A TypedDict could be used too, but the default
# values would not be explicit.
# pylint: disable=too-many-arguments, too-many-locals, too-many-statements
# pylint: disable=too-many-branches, line-too-long
def plot_disjunctive_graph(
    job_shop: JobShopGraph | JobShopInstance,
    *,
    title: str | None = None,
    figsize: tuple[float, float] = (6, 4),
    node_size: int = 1600,
    edge_width: int = 2,
    font_size: int = 10,
    arrow_size: int = 35,
    alpha: float = 0.95,
    operation_node_labeler: Callable[[Node], str] = duration_labeler,
    node_font_color: str = "white",
    machine_colors: dict[int, tuple[float, float, float, float]] | None = None,
    color_map: str = "Dark2_r",
    disjunctive_edge_color: str = "red",
    conjunctive_edge_color: str = "black",
    layout: Layout | None = None,
    draw_disjunctive_edges: bool | str = True,
    conjunctive_edges_additional_params: dict[str, Any] | None = None,
    disjunctive_edges_additional_params: dict[str, Any] | None = None,
    conjunctive_patch_label: str = "Conjunctive edges",
    disjunctive_patch_label: str = "Disjunctive edges",
    legend_text: str = "$p_{ij}=$duration of $O_{ij}$",
    show_machine_colors_in_legend: bool = True,
    machine_labels: Sequence[str] | None = None,
    legend_location: str = "upper left",
    legend_bbox_to_anchor: tuple[float, float] = (1.01, 1),
    start_node_label: str = "$S$",
    end_node_label: str = "$T$",
    font_family: str = "sans-serif",
) -> tuple[plt.Figure, plt.Axes]:
    r"""Plots the disjunctive graph of the given job shop instance or graph.

    Args:
        job_shop:
            The job shop instance or graph to plot. Can be either a
            :class:`JobShopGraph` or a :class:`JobShopInstance`. If a job shop
            instance is given, the disjunctive graph is built before plotting
            using the :func:`~job_shop_lib.graphs.build_disjunctive_graph`.
        title:
            The title of the graph (default is ``"Disjunctive Graph
            Visualization: {job_shop.instance.name}"``).
        figsize:
            The size of the figure (default is (6, 4)).
        node_size:
            The size of the nodes (default is 1600).
        edge_width:
            The width of the edges (default is 2).
        font_size:
            The font size of the node labels (default is 10).
        arrow_size:
            The size of the arrows (default is 35).
        alpha:
            The transparency level of the nodes and edges (default is 0.95).
        operation_node_labeler:
            A function that formats labels for operation nodes. Receives a
            :class:`~job_shop_lib.graphs.Node` and returns a string.
            The default is :func:`duration_labeler`, which labels the nodes
            with their duration.
        node_font_color:
            The color of the node labels (default is ``"white"``).
        machine_colors:
            A dictionary that maps machine ids to colors. If not provided,
            the colors are generated using the ``color_map``. If provided,
            the colors are used as the base for the node colors. The
            dictionary should have the form ``{machine_id: (r, g, b, a)}``.
            For source and sink nodes use ``-1`` as the machine id.
        color_map:
            The color map to use for the nodes (default is ``"Dark2_r"``).
        disjunctive_edge_color:
            The color of the disjunctive edges (default is ``"red"``).
        conjunctive_edge_color:
            The color of the conjunctive edges (default is ``"black"``).
        layout:
            The layout of the graph (default is ``graphviz_layout`` with
            ``prog="dot"`` and ``args="-Grankdir=LR"``). If not available,
            the spring layout is used. To install pygraphviz, check
            `pygraphviz documentation
            <https://pygraphviz.github.io/documentation/stable/install.html>`_.
        draw_disjunctive_edges:
            Whether to draw disjunctive edges (default is ``True``). If
            ``False``, only conjunctive edges are drawn. If ``"single_edge",``
            the disjunctive edges are drawn as undirected edges by removing one
            of the directions. If using this last option is recommended to set
            the "arrowstyle" parameter to ``"-"`` or ``"<->"`` in the
            ``disjunctive_edges_additional_params`` to make the edges look
            better. See `matplotlib documentation on arrow styles <https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.ArrowStyle.html#matplotlib.patches.ArrowStyle>`_
            and `nx.draw_networkx_edges <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx_edges.html>`_
            for more information.
        conjunctive_edges_additional_params:
            Additional parameters to pass to the conjunctive edges when
            drawing them (default is ``None``). See the documentation of
            `nx.draw_networkx_edges <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx_edges.html>`_
            for more information. The parameters that are explicitly set by
            this function and should not be part of this dictionary are
            ``edgelist``, ``pos``, ``width``, ``edge_color``, and
            ``arrowsize``.
        disjunctive_edges_additional_params:
            Same as ``conjunctive_edges_additional_params``, but for
            disjunctive edges (default is ``None``).
        conjunctive_patch_label:
            The label for the conjunctive edges in the legend (default is
            ``"Conjunctive edges"``).
        disjunctive_patch_label:
            The label for the disjunctive edges in the legend (default is
            ``"Disjunctive edges"``).
        legend_text:
            Text to display in the legend after the conjunctive and
            disjunctive edges labels (default is
            ``"$p_{ij}=$duration of $O_{ij}$"``).
        show_machine_colors_in_legend:
            Whether to show the colors of the machines in the legend
            (default is ``True``).
        machine_labels:
            The labels for the machines (default is
            ``[f"Machine {i}" for i in range(num_machines)]``). Not used if
            ``show_machine_colors_in_legend`` is ``False``.
        legend_location:
            The location of the legend (default is "upper left").
        legend_bbox_to_anchor:
            The anchor of the legend box (default is ``(1.01, 1)``).
        start_node_label:
            The label for the start node (default is ``"$S$"``).
        end_node_label:
            The label for the end node (default is ``"$T$"``).
        font_family:
            The font family of the node labels (default is ``"sans-serif"``).

    Returns:
        A matplotlib Figure object representing the disjunctive graph.

    Example:

        .. code-block:: python

            job_shop_instance = JobShopInstance(...)  # or a JobShopGraph
            fig = plot_disjunctive_graph(job_shop_instance)

    """  # noqa: E501

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
    operation_nodes = job_shop_graph.nodes_by_type[NodeType.OPERATION]
    cmap_func: matplotlib.colors.Colormap | None = None
    if machine_colors is None:
        machine_colors = {}
        cmap_func = matplotlib.colormaps.get_cmap(color_map)
        remaining_machines = job_shop_graph.instance.num_machines
        for operation_node in operation_nodes:
            if job_shop_graph.is_removed(operation_node.node_id):
                continue
            machine_id = operation_node.operation.machine_id
            if machine_id not in machine_colors:
                machine_colors[machine_id] = cmap_func(
                    (_get_node_color(operation_node) + 1)
                    / job_shop_graph.instance.num_machines
                )
                remaining_machines -= 1
            if remaining_machines == 0:
                break
        node_colors: list[Any] = [
            _get_node_color(node)
            for node in job_shop_graph.nodes
            if not job_shop_graph.is_removed(node.node_id)
        ]
    else:
        node_colors = []
        for node in job_shop_graph.nodes:
            if job_shop_graph.is_removed(node.node_id):
                continue
            if node.node_type == NodeType.OPERATION:
                machine_id = node.operation.machine_id
            else:
                machine_id = -1
            node_colors.append(machine_colors[machine_id])

    nx.draw_networkx_nodes(
        job_shop_graph.graph,
        pos,
        node_size=node_size,
        node_color=node_colors,
        alpha=alpha,
        cmap=cmap_func,
    )

    # Draw edges
    # ----------
    conjunctive_edges = [
        (u, v)
        for u, v, d in job_shop_graph.graph.edges(data=True)
        if d["type"] == EdgeType.CONJUNCTIVE
    ]
    disjunctive_edges: Iterable[tuple[int, int]] = [
        (u, v)
        for u, v, d in job_shop_graph.graph.edges(data=True)
        if d["type"] == EdgeType.DISJUNCTIVE
    ]
    if conjunctive_edges_additional_params is None:
        conjunctive_edges_additional_params = {}
    if disjunctive_edges_additional_params is None:
        disjunctive_edges_additional_params = {}

    nx.draw_networkx_edges(
        job_shop_graph.graph,
        pos,
        edgelist=conjunctive_edges,
        width=edge_width,
        edge_color=conjunctive_edge_color,
        arrowsize=arrow_size,
        **conjunctive_edges_additional_params,
    )

    if draw_disjunctive_edges:
        if draw_disjunctive_edges == "single_edge":
            # Filter the disjunctive edges to remove one of the directions
            disjunctive_edges_filtered = set()
            for u, v in disjunctive_edges:
                if u > v:
                    u, v = v, u
                disjunctive_edges_filtered.add((u, v))
            disjunctive_edges = disjunctive_edges_filtered
        nx.draw_networkx_edges(
            job_shop_graph.graph,
            pos,
            edgelist=disjunctive_edges,
            width=edge_width,
            edge_color=disjunctive_edge_color,
            arrowsize=arrow_size,
            **disjunctive_edges_additional_params,
        )

    # Draw node labels
    # ----------------
    labels = {}
    if job_shop_graph.nodes_by_type[NodeType.SOURCE]:
        source_node = job_shop_graph.nodes_by_type[NodeType.SOURCE][0]
        if not job_shop_graph.is_removed(source_node.node_id):
            labels[source_node] = start_node_label
    if job_shop_graph.nodes_by_type[NodeType.SINK]:
        sink_node = job_shop_graph.nodes_by_type[NodeType.SINK][0]
        # check if the sink node is removed
        if not job_shop_graph.is_removed(sink_node.node_id):
            labels[sink_node] = end_node_label
    for operation_node in operation_nodes:
        if job_shop_graph.is_removed(operation_node.node_id):
            continue
        labels[operation_node] = operation_node_labeler(operation_node)

    nx.draw_networkx_labels(
        job_shop_graph.graph,
        pos,
        labels=labels,
        font_color=node_font_color,
        font_size=font_size,
        font_family=font_family,
    )
    # Final touches
    # -------------
    plt.axis("off")
    plt.tight_layout()
    # Create a legend to indicate the meaning of the edge colors
    conjunctive_patch = matplotlib.patches.Patch(
        color=conjunctive_edge_color, label=conjunctive_patch_label
    )
    disjunctive_patch = matplotlib.patches.Patch(
        color=disjunctive_edge_color, label=disjunctive_patch_label
    )
    handles = [conjunctive_patch, disjunctive_patch]

    # Add machine colors to the legend
    if show_machine_colors_in_legend:
        label_color_pairs = []
        sorted_machine_colors = sorted(
            machine_colors.items(), key=lambda x: x[0]
        )
        for machine_id, color in sorted_machine_colors:
            label = None
            if machine_id == -1:
                continue
            if machine_labels is not None:
                label = machine_labels[machine_id]
            elif machine_id >= 0:
                label = f"Machine {machine_id}"

            if label:  # Add patch if a label was determined
                label_color_pairs.append((label, color))

        machine_patches = [
            matplotlib.patches.Patch(color=color, label=label)
            for label, color in sorted(label_color_pairs)
        ]
        handles.extend(machine_patches)

    # Add to the legend the meaning of m and d
    if legend_text:
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
        handles.append(extra)

    plt.legend(
        handles=handles,
        loc=legend_location,
        bbox_to_anchor=legend_bbox_to_anchor,
        borderaxespad=0.0,
    )
    return plt.gcf(), plt.gca()


def _get_node_color(node: Node) -> int:
    """Returns the color of the node."""
    if node.node_type == NodeType.SOURCE:
        return -1
    if node.node_type == NodeType.SINK:
        return -1
    if node.node_type == NodeType.OPERATION:
        return node.operation.machine_id

    raise ValidationError("Invalid node type.")
