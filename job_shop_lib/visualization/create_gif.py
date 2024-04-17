"""Module for creating a GIF of the schedule being built by a
dispatching rule solver."""

import os
import pathlib
import shutil
from typing import Callable

import imageio
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from job_shop_lib import JobShopInstance, Schedule, Operation
from job_shop_lib.dispatching import DispatchingRuleSolver, Dispatcher
from job_shop_lib.visualization.gantt_chart import plot_gantt_chart


# Most of the arguments are optional with default values. There is no way to
# reduce the number of arguments without losing functionality.
# pylint: disable=too-many-arguments
def create_gif(
    gif_path: str,
    instance: JobShopInstance,
    solver: DispatchingRuleSolver,
    plot_function: (
        Callable[[Schedule, int, list[Operation] | None], Figure] | None
    ) = None,
    fps: int = 1,
    remove_frames: bool = True,
    frames_dir: str | None = None,
    plot_current_time: bool = True,
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
        frames_dir, instance, solver, plot_function, plot_current_time
    )
    create_gif_from_frames(frames_dir, gif_path, fps)

    if remove_frames:
        shutil.rmtree(frames_dir)


def plot_gantt_chart_wrapper(
    title: str | None = None,
    cmap: str = "viridis",
    show_available_operations: bool = False,
) -> Callable[[Schedule, int, list[Operation] | None], Figure]:
    """Returns a function that plots a Gantt chart for an unfinished schedule.

    Args:
        title: The title of the Gantt chart.
        cmap: The name of the colormap to use.

    Returns:
        A function that plots a Gantt chart for a schedule. The function takes
        a `Schedule` object and the makespan of the schedule as input and
        returns a `Figure` object.
    """

    def plot_function(
        schedule: Schedule,
        makespan: int,
        available_operations: list | None = None,
    ) -> Figure:
        fig, ax = plot_gantt_chart(
            schedule, title=title, cmap_name=cmap, xlim=makespan
        )

        if not show_available_operations or available_operations is None:
            return fig

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
            bbox=dict(facecolor="white", alpha=0.5, boxstyle="round,pad=0.5"),
        )
        return fig

    return plot_function


def create_gantt_chart_frames(
    frames_dir: str,
    instance: JobShopInstance,
    solver: DispatchingRuleSolver,
    plot_function: Callable[[Schedule, int, list[Operation] | None], Figure],
    plot_current_time: bool = True,
) -> None:
    """Creates frames of the Gantt chart for the schedule being built.

    Args:
        frames_dir:
            The directory to save the frames in.
        instance:
            The instance of the job shop problem to be scheduled.
        solver:
            The dispatching rule solver to use.
        plot_function:
            A function that plots a Gantt chart for a schedule. It
            should take a `Schedule` object and the makespan of the schedule as
            input and return a `Figure` object.
        plot_current_time:
            Whether to plot a vertical line at the current time."""
    dispatcher = Dispatcher(instance, pruning_function=solver.pruning_function)
    schedule = dispatcher.schedule
    makespan = solver(instance).makespan()
    iteration = 0

    while not schedule.is_complete():
        solver.step(dispatcher)
        iteration += 1
        fig = plot_function(
            schedule,
            makespan,
            dispatcher.available_operations(),
        )
        current_time = (
            None if not plot_current_time else dispatcher.current_time()
        )
        _save_frame(fig, frames_dir, iteration, current_time)


def _save_frame(
    figure: Figure, frames_dir: str, number: int, current_time: int | None
) -> None:
    if current_time is not None:
        figure.gca().axvline(current_time, color="red", linestyle="--")

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
