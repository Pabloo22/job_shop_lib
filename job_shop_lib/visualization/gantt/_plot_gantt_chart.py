"""Module for plotting static Gantt charts for job shop schedules."""

from typing import Optional, List, Tuple, Dict

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Patch

from job_shop_lib import Schedule, ScheduledOperation

_BASE_Y_POSITION = 1
_Y_POSITION_INCREMENT = 10


def plot_gantt_chart(
    schedule: Schedule,
    title: Optional[str] = None,
    cmap_name: str = "viridis",
    xlim: Optional[int] = None,
    number_of_x_ticks: int = 15,
    job_labels: Optional[List[str]] = None,
    machine_labels: Optional[List[str]] = None,
    legend_title: str = "",
    x_label: str = "Time units",
    y_label: str = "Machines",
) -> Tuple[Figure, plt.Axes]:
    """Plots a Gantt chart for the schedule.

    This function generates a Gantt chart that visualizes the schedule of jobs
    across multiple machines. Each job is represented with a unique color,
    and operations are plotted as bars on the corresponding machines over time.

    The Gantt chart helps to understand the flow of jobs on machines and
    visualize the makespan of the schedule, i.e., the time it takes to
    complete all jobs.

    The Gantt chart includes:

    - X-axis: Time units, representing the progression of the schedule.
    - Y-axis: Machines, which are assigned jobs at various time slots.
    - Legend: A list of jobs, labeled and color-coded for clarity.

    .. note::
        The last tick on the x-axis always represents the makespan for easy
        identification of the completion time.

    Args:
        schedule:
            The schedule to plot.
        title:
            The title of the plot. If not provided, the title:
            ``f"Gantt Chart for {schedule.instance.name} instance"``
            is used. To remove the title, provide an empty string.
        cmap_name:
            The name of the colormap to use. Default is "viridis".
        xlim:
            The maximum value for the x-axis. If not provided, the makespan of
            the schedule is used.
        number_of_x_ticks:
            The number of ticks to use in the x-axis.
        job_labels:
            A list of labels for each job. If ``None``, the labels are
            automatically generated as "Job 0", "Job 1", etc.
        machine_labels:
            A list of labels for each machine. If ``None``, the labels are
            automatically generated as "0", "1", etc.
        legend_title:
            The title of the legend. If not provided, the legend will not have
            a title.
        x_label:
            The label for the x-axis. Default is "Time units". To remove the
            label, provide an empty string.
        y_label:
            The label for the y-axis. Default is "Machines". To remove the
            label, provide an empty string.

    Returns:
        - A ``matplotlib.figure.Figure`` object.
        - A ``matplotlib.axes.Axes`` object where the Gantt chart is plotted.
    """
    fig, ax = _initialize_plot(schedule, title, x_label, y_label)
    legend_handles = _plot_machine_schedules(
        schedule, ax, cmap_name, job_labels
    )
    _configure_legend(ax, legend_handles, legend_title)
    _configure_axes(schedule, ax, xlim, number_of_x_ticks, machine_labels)
    return fig, ax


def _initialize_plot(
    schedule: Schedule,
    title: Optional[str],
    x_label: str = "Time units",
    y_label: str = "Machines",
) -> Tuple[Figure, plt.Axes]:
    """Initializes the plot."""
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True, which="both", axis="x", linestyle="--", linewidth=0.5)
    ax.yaxis.grid(False)
    if title is None:
        title = f"Gantt Chart for {schedule.instance.name} instance"
    plt.title(title)
    return fig, ax


def _plot_machine_schedules(
    schedule: Schedule,
    ax: plt.Axes,
    cmap_name: str,
    job_labels: Optional[List[str]],
) -> Dict[int, Patch]:
    """Plots the schedules for each machine."""
    max_job_id = schedule.instance.num_jobs - 1
    cmap = plt.get_cmap(cmap_name, max_job_id + 1)
    norm = Normalize(vmin=0, vmax=max_job_id)
    legend_handles = {}

    for machine_index, machine_schedule in enumerate(schedule.schedule):
        y_position_for_machines = (
            _BASE_Y_POSITION + _Y_POSITION_INCREMENT * machine_index
        )

        for scheduled_op in machine_schedule:
            color = cmap(norm(scheduled_op.job_id))
            _plot_scheduled_operation(
                ax, scheduled_op, y_position_for_machines, color
            )
            if scheduled_op.job_id not in legend_handles:
                legend_handles[scheduled_op.job_id] = Patch(
                    facecolor=color,
                    label=_get_job_label(job_labels, scheduled_op.job_id),
                )

    return legend_handles


def _get_job_label(job_labels: Optional[List[str]], job_id: int) -> str:
    """Returns the label for the job."""
    if job_labels is None:
        return f"Job {job_id}"
    return job_labels[job_id]


def _plot_scheduled_operation(
    ax: plt.Axes,
    scheduled_op: ScheduledOperation,
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


def _configure_legend(
    ax: plt.Axes, legend_handles: Dict[int, Patch], legend_title: str
):
    """Configures the legend for the plot."""
    sorted_legend_handles = [
        legend_handles[job_id] for job_id in sorted(legend_handles)
    ]
    ax.legend(
        handles=sorted_legend_handles,
        loc="upper left",
        bbox_to_anchor=(1, 1),
        title=legend_title,
    )


def _configure_axes(
    schedule: Schedule,
    ax: plt.Axes,
    xlim: Optional[int],
    number_of_x_ticks: int,
    machine_labels: list[str] | None,
):
    """Sets the limits and labels for the axes."""
    num_machines = len(schedule.schedule)
    ax.set_ylim(0, _BASE_Y_POSITION + _Y_POSITION_INCREMENT * num_machines)
    ax.set_yticks(
        [
            _BASE_Y_POSITION
            + _Y_POSITION_INCREMENT // 2
            + _Y_POSITION_INCREMENT * i
            for i in range(num_machines)
        ]
    )
    if machine_labels is None:
        machine_labels = [str(i) for i in range(num_machines)]
    ax.set_yticklabels(machine_labels)
    makespan = schedule.makespan()
    xlim = xlim if xlim is not None else makespan
    ax.set_xlim(0, xlim)

    tick_interval = max(1, xlim // number_of_x_ticks)
    xticks = list(range(0, xlim + 1, tick_interval))

    if xticks[-1] != xlim:
        xticks.pop()
        xticks.append(xlim)

    ax.set_xticks(xticks)
