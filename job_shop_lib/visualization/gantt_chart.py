from typing import Optional

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Patch

from job_shop_lib import Schedule


def plot_gantt_chart(
    schedule: Schedule,
    title: Optional[str] = None,
    cmap_name: str = "viridis",
    xlim: Optional[int] = None,
) -> tuple[Figure, plt.Axes]:
    """Plots a Gantt chart for the schedule."""
    fig, ax = _initialize_plot(schedule, title)
    legend_handles = _plot_machine_schedules(schedule, ax, cmap_name)
    _configure_legend(ax, legend_handles)
    _configure_axes(schedule, ax, xlim)
    return fig, ax


def _initialize_plot(
    schedule, title: Optional[str]
) -> tuple[Figure, plt.Axes]:
    """Initializes the plot."""
    fig, ax = plt.subplots()
    ax.set_xlabel("Time units")
    ax.set_ylabel("Machines")
    ax.grid(True, which="both", axis="x", linestyle="--", linewidth=0.5)
    ax.yaxis.grid(False)
    if title is None:
        title = f"Gantt Chart for {schedule.instance.name} instance"
    plt.title(title)
    return fig, ax


def _plot_machine_schedules(
    schedule: Schedule, ax: plt.Axes, cmap_name: str
) -> dict[int, Patch]:
    """Plots the schedules for each machine."""
    max_job_id = schedule.instance.num_jobs - 1
    cmap = plt.cm.get_cmap(cmap_name, max_job_id + 1)
    norm = Normalize(vmin=0, vmax=max_job_id)
    legend_handles = {}

    for machine_index, machine_schedule in enumerate(schedule.schedule):
        y_position_for_machines = 10 + 10 * machine_index

        for scheduled_op in machine_schedule:
            color = cmap(norm(scheduled_op.job_id))
            _plot_scheduled_operation(
                ax, scheduled_op, y_position_for_machines, color
            )
            if scheduled_op.job_id not in legend_handles:
                legend_handles[scheduled_op.job_id] = Patch(
                    facecolor=color, label=f"Job {scheduled_op.job_id + 1}"
                )

    return legend_handles


def _plot_scheduled_operation(
    ax: plt.Axes,
    scheduled_op,
    y_position_for_machines: int,
    color,
):
    """Plots a single scheduled operation."""
    start_time, end_time = scheduled_op.start_time, scheduled_op.end_time
    duration = end_time - start_time
    ax.broken_barh(
        [(start_time, duration)],
        (y_position_for_machines, 9),
        facecolors=color,
    )


def _configure_legend(ax: plt.Axes, legend_handles: dict[int, Patch]):
    """Configures the legend for the plot."""
    sorted_legend_handles = [
        legend_handles[job_id] for job_id in sorted(legend_handles)
    ]
    ax.legend(handles=sorted_legend_handles, loc="lower right")


def _configure_axes(schedule: Schedule, ax: plt.Axes, xlim: Optional[int]):
    """Sets the limits and labels for the axes."""
    num_machines = len(schedule.schedule)
    ax.set_ylim(0, 10 + 10 * num_machines)
    ax.set_yticks([15 + 10 * i for i in range(num_machines)])
    ax.set_yticklabels([str(i + 1) for i in range(num_machines)])
    xlim = xlim if xlim is not None else schedule.makespan() + 1
    ax.set_xlim(0, xlim)
