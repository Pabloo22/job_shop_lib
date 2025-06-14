import pytest

from job_shop_lib.graphs import (
    build_resource_task_graph,
    build_resource_task_graph_with_jobs,
    build_complete_resource_task_graph,
)
from job_shop_lib.visualization.graphs import (
    plot_resource_task_graph,
    three_columns_layout,
)


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_resource_task_graph(example_job_shop_instance):
    graph = build_resource_task_graph(example_job_shop_instance)
    fig = plot_resource_task_graph(graph)

    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_resource_task_graph_with_jobs(example_job_shop_instance):
    graph = build_resource_task_graph_with_jobs(example_job_shop_instance)
    fig = plot_resource_task_graph(graph)

    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_complete_resource_task_graph(example_job_shop_instance):
    graph = build_complete_resource_task_graph(example_job_shop_instance)
    fig = plot_resource_task_graph(graph)
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_resource_task_graph_custom_title_legend(
    example_job_shop_instance,
):
    graph = build_resource_task_graph(example_job_shop_instance)
    fig = plot_resource_task_graph(
        graph,
        title="Custom Title for Resource Task Graph",
        figsize=(8, 8),
        add_legend=True,
        legend_text="Custom legend text",
    )
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_resource_task_graph_with_jobs_doble_arrow(
    example_job_shop_instance,
):
    with_jobs_graph = build_resource_task_graph_with_jobs(
        example_job_shop_instance
    )
    fig = plot_resource_task_graph(
        with_jobs_graph,
        title="",
        figsize=(5, 7),
        draw_only_one_edge=True,
        edge_additional_params={
            "arrowstyle": "<|-|>",
            "arrowsize": 10,
            "connectionstyle": "arc3,rad=0.1",
            "width": 1.5,
            "edge_color": "salmon",
        },
        default_node_color="gray",
        node_font_color="white",
    )
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_resource_task_graph_with_jobs_single_edge_custom_params(
    example_job_shop_instance,
):
    graph = build_resource_task_graph_with_jobs(example_job_shop_instance)
    fig = plot_resource_task_graph(
        graph,
        draw_only_one_edge=True,
        edge_additional_params={
            "arrowstyle": "-|>",
            "arrowsize": 15,
            "edge_color": "purple",
            "width": 2,
        },
        node_size=1500,
    )
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_complete_resource_task_graph_custom_shapes_colors_layout(
    example_job_shop_instance,
):
    graph = build_complete_resource_task_graph(example_job_shop_instance)
    custom_layout = three_columns_layout(
        graph, leftmost_position=0.2, rightmost_position=0.8
    )
    fig = plot_resource_task_graph(
        graph,
        layout=custom_layout,
        node_shapes={
            "machine": "p",  # pentagon
            "job": "h",  # hexagon
            "operation": ">",  # triangle_right
            "global": "d",  # diamond
        },
        machine_color_map_name="viridis",
        default_node_color="lightcoral",
        node_font_color="blue",
        font_size=8,
    )
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_complete_resource_task_graph_custom_edge_params(
    example_job_shop_instance,
):
    graph = build_complete_resource_task_graph(
        example_job_shop_instance
    )
    fig = plot_resource_task_graph(
        graph,
        title="",
        figsize=(4, 7),
        draw_only_one_edge=True,
        edge_additional_params={
            "arrowstyle": "<|-|>",
            "arrowsize": 10,
            "connectionstyle": "arc3,rad=0.15",
            "width": 1.5,
            "edge_color": "k",
        },
        node_font_color="k",
        alpha=0.9,
        layout=three_columns_layout(
            graph,
            leftmost_position=0.45,  # Move left column more rigth
        ),
    )
    return fig


if __name__ == "__main__":
    pytest.main(["-v", __file__])
