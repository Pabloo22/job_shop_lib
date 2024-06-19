"""Module for creating a GIF of the schedule being built by a
dispatching rule solver."""

import os
import pathlib
import shutil
from collections.abc import Callable
from typing import Sequence

import imageio
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from job_shop_lib import (
    JobShopInstance,
    Schedule,
    Operation,
    ScheduledOperation,
    ValidationError,
)
from job_shop_lib.dispatching import (
    DispatchingRuleSolver,
    Dispatcher,
    HistoryTracker,
)
from job_shop_lib.visualization.gantt_chart import plot_gantt_chart


PlotFunction = Callable[
    [Schedule, int | None, list[Operation] | None, int | None], Figure
]


# Most of the arguments are optional with default values. There is no way to
# reduce the number of arguments without losing functionality.
# pylint: disable=too-many-arguments
def create_gif(
    gif_path: str,
    instance: JobShopInstance,
    solver: DispatchingRuleSolver | None = None,
    plot_function: PlotFunction | None = None,
    fps: int = 1,
    remove_frames: bool = True,
    frames_dir: str | None = None,
    plot_current_time: bool = True,
    schedule_history: Sequence[ScheduledOperation] | None = None,
) -> None:
    """Creates a GIF of the schedule being built by the given solver.

    Args:
        gif_path:
            The path to save the GIF file. It should end with ".gif".
        instance:
            The instance of the job shop problem to be scheduled.
        solver:
            The dispatching rule solver to use.
        plot_function:
            A function that plots a Gantt chart for a schedule. It
            should take a `Schedule` object and the makespan of the schedule as
            input and return a `Figure` object. If not provided, a default
            function is used.
        fps:
            The number of frames per second in the GIF.
        remove_frames:
            Whether to remove the frames after creating the GIF.
        frames_dir:
            The directory to save the frames in. If not provided,
            `gif_path.replace(".gif", "") + "_frames"` is used.
        plot_current_time:
            Whether to plot a vertical line at the current time.
    """
    if plot_function is None:
        plot_function = plot_gantt_chart_wrapper()

    if frames_dir is None:
        # Use the name of the GIF file as the directory name
        frames_dir = gif_path.replace(".gif", "") + "_frames"
    path = pathlib.Path(frames_dir)
    path.mkdir(exist_ok=True)
    frames_dir = str(path)
    create_gantt_chart_frames(
        frames_dir,
        instance,
        solver,
        plot_function,
        plot_current_time,
        schedule_history,
    )
    create_gif_from_frames(frames_dir, gif_path, fps)

    if remove_frames:
        shutil.rmtree(frames_dir)


def plot_gantt_chart_wrapper(
    title: str | None = None,
    cmap: str = "viridis",
    show_available_operations: bool = False,
) -> PlotFunction:
    """Returns a function that plots a Gantt chart for an unfinished schedule.

    Args:
        title: The title of the Gantt chart.
        cmap: The name of the colormap to use.
        show_available_operations:
            Whether to show the available operations in the Gantt chart.

    Returns:
        A function that plots a Gantt chart for a schedule. The function takes
        the following arguments:
        - schedule: The schedule to plot.
        - makespan: The makespan of the schedule.
        - available_operations: A list of available operations. If None,
            the available operations are not shown.
        - current_time: The current time in the schedule. If provided, a
            red vertical line is plotted at this time.
    """

    def plot_function(
        schedule: Schedule,
        makespan: int | None = None,
        available_operations: list | None = None,
        current_time: int | None = None,
    ) -> Figure:
        fig, ax = plot_gantt_chart(
            schedule, title=title, cmap_name=cmap, xlim=makespan
        )

        if show_available_operations and available_operations is not None:

            operations_text = "\n".join(
                str(operation) for operation in available_operations
            )
            text = f"Available operations:\n{operations_text}"
            # Print the available operations at the bottom right corner
            # of the Gantt chart
            fig.text(
                1.25,
                0.05,
                text,
                ha="right",
                va="bottom",
                transform=ax.transAxes,
                bbox={
                    "facecolor": "white",
                    "alpha": 0.5,
                    "boxstyle": "round,pad=0.5",
                },
            )
        if current_time is not None:
            ax.axvline(current_time, color="red", linestyle="--")
        return fig

    return plot_function


def create_gantt_chart_frames(
    frames_dir: str,
    instance: JobShopInstance,
    solver: DispatchingRuleSolver | None,
    plot_function: PlotFunction,
    plot_current_time: bool = True,
    schedule_history: Sequence[ScheduledOperation] | None = None,
) -> None:
    """Creates frames of the Gantt chart for the schedule being built.

    Args:
        frames_dir:
            The directory to save the frames in.
        instance:
            The instance of the job shop problem to be scheduled.
        solver:
            The dispatching rule solver to use. If not provided, the history
            of scheduled operations should be provided.
        plot_function:
            A function that plots a Gantt chart for a schedule. It
            should take a `Schedule` object and the makespan of the schedule as
            input and return a `Figure` object.
        plot_current_time:
            Whether to plot a vertical line at the current time.
        scheduled_history:
            A sequence of scheduled operations. If not provided, the solver
    """
    if solver is not None and schedule_history is None:
        dispatcher = Dispatcher(
            instance, pruning_function=solver.pruning_function
        )
        history_tracker = HistoryTracker(dispatcher)
        makespan = solver.solve(instance, dispatcher).makespan()
        dispatcher.unsubscribe(history_tracker)
        dispatcher.reset()
        schedule_history = history_tracker.history
    elif schedule_history is not None and solver is None:
        dispatcher = Dispatcher(instance)
        makespan = max(
            scheduled_operation.end_time
            for scheduled_operation in schedule_history
        )
    elif schedule_history is not None and solver is not None:
        raise ValidationError(
            "Only one of 'solver' and 'history' should be provided."
        )
    else:
        raise ValidationError(
            "Either 'solver' or 'history' should be provided."
        )

    for i, scheduled_operation in enumerate(schedule_history, start=1):
        dispatcher.dispatch(
            scheduled_operation.operation, scheduled_operation.machine_id
        )
        current_time = (
            None if not plot_current_time else dispatcher.current_time()
        )
        fig = plot_function(
            dispatcher.schedule,
            makespan,
            dispatcher.available_operations(),
            current_time,
        )
        _save_frame(fig, frames_dir, i)


def _save_frame(figure: Figure, frames_dir: str, number: int) -> None:
    figure.savefig(f"{frames_dir}/frame_{number:02d}.png", bbox_inches="tight")
    plt.close(figure)


def create_gif_from_frames(frames_dir: str, gif_path: str, fps: int) -> None:
    """Creates a GIF from the frames in the given directory.

    Args:
        frames_dir:
            The directory containing the frames to be used in the GIF.
        gif_path:
            The path to save the GIF file. It should end with ".gif".
        fps:
            The number of frames per second in the GIF.
    """
    frames = [
        os.path.join(frames_dir, frame)
        for frame in sorted(os.listdir(frames_dir))
    ]
    images = [imageio.imread(frame) for frame in frames]
    imageio.mimsave(gif_path, images, fps=fps, loop=0)
