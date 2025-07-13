import pytest
from matplotlib.figure import Figure
import matplotlib

from job_shop_lib import Schedule
from job_shop_lib.visualization.gantt import plot_gantt_chart

# Skip all tests in this file if Tkinter is missing
try:
    import tkinter
except ImportError:
    pytest.skip("Tkinter is not available, skipping plot tests.", allow_module_level=True)


matplotlib.use("Agg")

@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_gantt_chart_default(example_schedule: Schedule):
    fig, ax = plot_gantt_chart(example_schedule)
    assert isinstance(fig, Figure)
    assert ax is not None
    # Further assertions can be visual via mpl_image_compare
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_gantt_chart_custom_title(example_schedule: Schedule):
    fig, ax = plot_gantt_chart(example_schedule, title="Custom Title")
    assert isinstance(fig, Figure)
    assert ax is not None
    assert ax.get_title() == "Custom Title"
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_gantt_chart_no_title(example_schedule: Schedule):
    fig, ax = plot_gantt_chart(example_schedule, title="")
    assert isinstance(fig, Figure)
    assert ax is not None
    assert ax.get_title() == ""
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_gantt_chart_custom_labels(example_schedule: Schedule):
    job_labels = ["Job A", "Job B", "Job C"]
    # Assuming example_schedule has 3 machines based on conftest.py
    machine_labels = ["Machine X", "Machine Y", "Machine Z"]
    fig, ax = plot_gantt_chart(
        example_schedule,
        job_labels=job_labels,
        machine_labels=machine_labels,
        legend_title="Custom Legend",
        x_label="Custom X Label",
        y_label="Custom Y Label",
    )
    assert isinstance(fig, Figure)
    assert ax is not None
    assert ax.get_xlabel() == "Custom X Label"
    assert ax.get_ylabel() == "Custom Y Label"
    assert ax.get_legend().get_title().get_text() == "Custom Legend"

    # Check if machine labels are correctly set
    actual_machine_labels = [tick.get_text() for tick in ax.get_yticklabels()]
    assert actual_machine_labels == machine_labels

    # Check if job labels are correctly set in the legend
    legend_texts = [text.get_text() for text in ax.get_legend().get_texts()]
    assert legend_texts == job_labels

    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_gantt_chart_custom_xlim_and_ticks(example_schedule: Schedule):
    # Makespan of example_schedule is 9
    custom_xlim = 20
    num_ticks = 10
    fig, ax = plot_gantt_chart(
        example_schedule, xlim=custom_xlim, number_of_x_ticks=num_ticks
    )
    assert isinstance(fig, Figure)
    assert ax is not None
    assert ax.get_xlim() == (0, custom_xlim)
    # Check number of ticks (matplotlib might adjust slightly, so check >=)
    # Also, the last tick is always the xlim value.
    assert len(ax.get_xticks()) >= num_ticks
    assert ax.get_xticks()[-1] == custom_xlim
    return fig


@pytest.mark.mpl_image_compare(
    style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"}
)
def test_plot_gantt_chart_different_cmap(example_schedule: Schedule):
    fig, ax = plot_gantt_chart(example_schedule, cmap_name="plasma")
    assert isinstance(fig, Figure)
    assert ax is not None
    # Verification of cmap is primarily visual via mpl_image_compare
    return fig


if __name__ == "__main__":
    pytest.main(["-v", __file__])
