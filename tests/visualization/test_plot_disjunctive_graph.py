import pytest

from job_shop_lib.visualization import plot_disjunctive_graph


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_disjunctive_graph(example_job_shop_instance):
    fig, _ = plot_disjunctive_graph(example_job_shop_instance)

    return fig


if __name__ == "__main__":
    pytest.main(["-v", __file__])
