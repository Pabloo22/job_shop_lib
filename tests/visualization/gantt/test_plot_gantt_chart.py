import pytest
from matplotlib.figure import Figure
import matplotlib
import os
import tempfile
from PIL import Image

from job_shop_lib import Schedule
from job_shop_lib.visualization.gantt import plot_gantt_chart
from job_shop_lib.visualization.gantt import _gantt_chart_video_and_gif_creation as gif_utils

# Skip all tests in this file if Tkinter is missing
try:
    import tkinter
except ImportError:
    pytest.skip("Tkinter is not available, skipping plot tests.", allow_module_level=True)

matplotlib.use("Agg")

@pytest.mark.mpl_image_compare(style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"})
def test_plot_gantt_chart_default(example_schedule: Schedule):
    fig, ax = plot_gantt_chart(example_schedule)
    assert isinstance(fig, Figure)
    assert ax is not None
    return fig

@pytest.mark.mpl_image_compare(style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"})
def test_plot_gantt_chart_custom_title(example_schedule: Schedule):
    fig, ax = plot_gantt_chart(example_schedule, title="Custom Title")
    assert isinstance(fig, Figure)
    assert ax is not None
    assert ax.get_title() == "Custom Title"
    return fig

@pytest.mark.mpl_image_compare(style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"})
def test_plot_gantt_chart_no_title(example_schedule: Schedule):
    fig, ax = plot_gantt_chart(example_schedule, title="")
    assert isinstance(fig, Figure)
    assert ax is not None
    assert ax.get_title() == ""
    return fig

@pytest.mark.mpl_image_compare(style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"})
def test_plot_gantt_chart_custom_labels(example_schedule: Schedule):
    job_labels = ["Job A", "Job B", "Job C"]
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
    assert [tick.get_text() for tick in ax.get_yticklabels()] == machine_labels
    assert [text.get_text() for text in ax.get_legend().get_texts()] == job_labels
    return fig

@pytest.mark.mpl_image_compare(style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"})
def test_plot_gantt_chart_custom_xlim_and_ticks(example_schedule: Schedule):
    custom_xlim = 20
    num_ticks = 10
    fig, ax = plot_gantt_chart(
        example_schedule, xlim=custom_xlim, number_of_x_ticks=num_ticks
    )
    assert isinstance(fig, Figure)
    assert ax is not None
    assert ax.get_xlim() == (0, custom_xlim)
    assert len(ax.get_xticks()) >= num_ticks
    assert ax.get_xticks()[-1] == custom_xlim
    return fig

@pytest.mark.mpl_image_compare(style="default", savefig_kwargs={"dpi": 300, "bbox_inches": "tight"})
def test_plot_gantt_chart_different_cmap(example_schedule: Schedule):
    fig, ax = plot_gantt_chart(example_schedule, cmap_name="plasma")
    assert isinstance(fig, Figure)
    assert ax is not None
    return fig

# New test for create_gif_from_gantt_frames
@pytest.fixture
def temp_frame_folder():
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(3):
            img = Image.new("RGB", (640, 480), color=(i * 80, i * 80, i * 80))
            img.save(os.path.join(tmpdir, f"frame_{i}.png"))
        yield tmpdir

def test_create_gif_from_gantt_frames(temp_frame_folder):
    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, "gantt.gif")

        gif_utils.create_gif_from_frames(
            frames_dir=temp_frame_folder,
            gif_path=output_path,
            fps=7,
            loop=1,
        )

        assert os.path.exists(output_path)
        assert output_path.endswith(".gif")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
