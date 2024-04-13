import pytest

from job_shop_lib.visualization import plot_disjunctive_graph
from job_shop_lib.graphs import build_disjunctive_graph


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_disjunctive_graph(example_job_shop_instance):
    graph = build_disjunctive_graph(example_job_shop_instance)
    fig = plot_disjunctive_graph(graph)

    return fig
