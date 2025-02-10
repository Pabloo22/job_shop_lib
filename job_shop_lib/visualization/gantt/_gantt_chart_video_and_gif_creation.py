"""Module for creating a GIF or a video of the schedule being built."""

import os
import pathlib
import shutil
from typing import Sequence, Protocol, Optional, List

import imageio
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

from job_shop_lib import (
    JobShopInstance,
    Schedule,
    Operation,
    ScheduledOperation,
)
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import (
    Dispatcher,
    HistoryObserver,
)
from job_shop_lib.dispatching.rules import DispatchingRuleSolver
from job_shop_lib.visualization.gantt._plot_gantt_chart import plot_gantt_chart


# This class serves as a more meaningful type hint than simply:
# PlotFunction = Callable[
#     [Schedule, int | None, list[Operation] | None, int | None], Figure
# ]
# That's why it doesn't have more methods or attributes. It is a protocol
# for functions, not for classes.
# pylint: disable=too-few-public-methods
class PartialGanttChartPlotter(Protocol):
    """A protocol for a function that plots an uncompleted Gantt chart
    for a schedule.

    This kind of functions are created using the
    :func:`plot_gantt_chart_wrapper` function.
    """

    def __call__(
        self,
        schedule: Schedule,
        makespan: Optional[int] = None,
        available_operations: Optional[List[Operation]] = None,
        current_time: Optional[int] = None,
    ) -> Figure:
        """Plots a Gantt chart for an unfinished schedule.

        Args:
            schedule:
                The schedule to plot.
            makespan:
                The makespan of the schedule if known. Can be used to fix
                the x-axis limits.
            available_operations:
                A list of available operations. If ``None``,
                the available operations are not shown.
            current_time:
                The current time in the schedule. If provided, a red
                vertical line is plotted at this time.
        """


def get_partial_gantt_chart_plotter(
    title: Optional[str] = None,
    cmap: str = "viridis",
    show_available_operations: bool = False,
) -> PartialGanttChartPlotter:
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
        makespan: Optional[int] = None,
        available_operations: Optional[List[Operation]] = None,
        current_time: Optional[int] = None,
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


# Most of the arguments are optional with default values. There is no way to
# reduce the number of arguments without losing functionality.
# pylint: disable=too-many-arguments
def create_gantt_chart_gif(
    instance: JobShopInstance,
    gif_path: Optional[str] = None,
    solver: Optional[DispatchingRuleSolver] = None,
    plot_function: Optional[PartialGanttChartPlotter] = None,
    fps: int = 1,
    remove_frames: bool = True,
    frames_dir: Optional[str] = None,
    plot_current_time: bool = True,
    schedule_history: Optional[Sequence[ScheduledOperation]] = None,
) -> None:
    """Creates a GIF of the schedule being built.

    Args:
        instance:
            The instance of the job shop problem to be scheduled.
        gif_path:
            The path to save the GIF file. It should end with ".gif". If not
            provided, the name of the instance is used.
        solver:
            The dispatching rule solver to use. If not provided, the history
            of scheduled operations should be provided.
        plot_function:
            A :class:`PlotFunction` that plots a Gantt chart for a schedule. It
            should take a `Schedule` object and the makespan of the schedule as
            input and return a `Figure` object. If not provided, a default
            function is used.
        fps:
            The number of frames per second in the GIF.
        remove_frames:
            Whether to remove the frames after creating the GIF.
        frames_dir:
            The directory to save the frames in. If not provided,
            ``gif_path.replace(".gif", "") + "_frames"`` is used.
        plot_current_time:
            Whether to plot a vertical line at the current time.
        schedule_history:
            A sequence of scheduled operations. If not provided, the solver
            will be used to generate the history.
    """
    if gif_path is None:
        gif_path = f"{instance.name}_gantt_chart.gif"

    if plot_function is None:
        plot_function = get_partial_gantt_chart_plotter()

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


# Most of the arguments are optional with default values. There is no way to
# reduce the number of arguments without losing functionality.
# pylint: disable=too-many-arguments
def create_gantt_chart_video(
    instance: JobShopInstance,
    video_path: Optional[str] = None,
    solver: Optional[DispatchingRuleSolver] = None,
    plot_function: Optional[PartialGanttChartPlotter] = None,
    fps: int = 1,
    remove_frames: bool = True,
    frames_dir: Optional[str] = None,
    plot_current_time: bool = True,
    schedule_history: Optional[Sequence[ScheduledOperation]] = None,
) -> None:
    """Creates a video of the schedule being built.

    Args:
        instance:
            The instance of the job shop problem to be scheduled.
        video_path:
            The path to save the video file.
        solver:
            The dispatching rule solver to use. If not provided, the history
            of scheduled operations should be provided.
        plot_function:
            A function that plots a Gantt chart for a schedule. It
            should take a :class:`Schedule` object and the makespan of the
            schedule as input and return a ``Figure`` object. If not provided,
            a default function is used.
        fps:
            The number of frames per second in the video.
        remove_frames:
            Whether to remove the frames after creating the video.
        frames_dir:
            The directory to save the frames in. If not provided,
            ``name_without_the_extension + "_frames"`` is used.
        plot_current_time:
            Whether to plot a vertical line at the current time.
        schedule_history:
            A sequence of scheduled operations. If not provided, the solver
            will be used to generate the history.
    """
    if video_path is None:
        video_path = f"{instance.name}_gantt_chart.mp4"

    if plot_function is None:
        plot_function = get_partial_gantt_chart_plotter()

    if frames_dir is None:
        extension = video_path.split(".")[-1]
        frames_dir = video_path.replace(f".{extension}", "") + "_frames"
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
    create_video_from_frames(frames_dir, video_path, fps)

    if remove_frames:
        shutil.rmtree(frames_dir)


def create_gantt_chart_frames(
    frames_dir: str,
    instance: JobShopInstance,
    solver: Optional[DispatchingRuleSolver],
    plot_function: PartialGanttChartPlotter,
    plot_current_time: bool = True,
    schedule_history: Optional[Sequence[ScheduledOperation]] = None,
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
            instance, ready_operations_filter=solver.ready_operations_filter
        )
        history_tracker = HistoryObserver(dispatcher)
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


def create_gif_from_frames(
    frames_dir: str, gif_path: str, fps: int, loop: int = 0
) -> None:
    """Creates a GIF or video from the frames in the given directory.

    Args:
        frames_dir:
            The directory containing the frames to be used in the GIF.
        gif_path:
            The path to save the GIF file. It should end with ".gif".
        fps:
            The number of frames per second in the GIF.
        loop:
            The number of times the GIF should loop. Default is 0, which means
            the GIF will loop indefinitely. If set to 1, the GIF will loop
            once. Added in version 0.6.0.
    """
    images = _load_images(frames_dir)
    imageio.mimsave(gif_path, images, fps=fps, loop=loop)


def create_video_from_frames(
    frames_dir: str, gif_path: str, fps: int, macro_block_size: int = 16
) -> None:
    """Creates a GIF or video from the frames in the given directory.

    Args:
        frames_dir:
            The directory containing the frames to be used in the video.
        gif_path:
            The path to save the video.
        fps:
            The number of frames per second.
    """
    images = _load_images(frames_dir)
    resized_images = [
        resize_image_to_macro_block(image, macro_block_size=macro_block_size)
        for image in images
    ]
    imageio.mimsave(
        gif_path, resized_images, fps=fps  # type: ignore[arg-type]
    )


def resize_image_to_macro_block(
    image: np.ndarray, macro_block_size: int = 16
) -> np.ndarray:
    """Resizes the image to ensure its dimensions are divisible by the macro
    block size.

    Args:
        image (numpy.ndarray): The input image.
        macro_block_size (int): The macro block size, typically 16.

    Returns:
        numpy.ndarray: The resized image.
    """
    height, width, channels = image.shape
    new_height = (
        (height + macro_block_size - 1) // macro_block_size * macro_block_size
    )
    new_width = (
        (width + macro_block_size - 1) // macro_block_size * macro_block_size
    )

    if (new_height, new_width) != (height, width):
        resized_image = np.zeros(
            (new_height, new_width, channels), dtype=image.dtype
        )
        resized_image[:height, :width] = image
        return resized_image
    return image


def _load_images(frames_dir: str) -> List:
    frames = [
        os.path.join(frames_dir, frame)
        for frame in sorted(os.listdir(frames_dir))
    ]
    return [imageio.imread(frame) for frame in frames]
