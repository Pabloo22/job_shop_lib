"""Home of the `GanttChartCreator` class."""

from typing import TypedDict, Required

import matplotlib.pyplot as plt

from job_shop_lib.dispatching import HistoryObserver
from job_shop_lib.visualization import (
    create_gantt_chart_video,
    plot_gantt_chart_wrapper,
    create_gif,
)

class GanttChartWrapperConfig(TypedDict, total=False):
    """Configuration for creating the plot function with the
    `plot_gantt_chart_wrapper` function."""

    title: str | None
    cmap: str
    show_available_operations: bool


class GifConfig(TypedDict, total=False):
    """Configuration for creating the GIF using the `create_gannt_chart_video`
    function."""

    gif_path: Required[str | None]
    fps: int
    remove_frames: bool
    frames_dir: str | None
    plot_current_time: bool


class VideoConfig(TypedDict, total=False):
    """Configuration for creating the video using the
    `create_gannt_chart_video` function."""

    video_path: str | None
    fps: int
    remove_frames: bool
    frames_dir: str | None
    plot_current_time: bool


class GanttChartCreator:
    """Facade class that centralizes the creation of Gantt charts and GIFs.

    It leverages a HistoryTracker to keep track of the operations being
    scheduled and provides methods to plot the current state
    of the schedule as a Gantt chart and to create a GIF that shows the
    evolution of the schedule over time.

    Attributes:
        history_observer:
            The history observer observing the dispatcher's state.
        gantt_chart_config:
            Configuration for plotting the Gantt chart.
        gif_config:
            Configuration for creating the GIF.
        gantt_chart_wrapper_config:
            Configuration for the Gantt chart wrapper function.
        video_config:
            Configuration for creating the video.
        plot_function:
            The function used to plot the Gantt chart when creating the GIF
            or video. Created using the `plot_gantt_chart_wrapper` function.
    """

    def __init__(
        self,
        history_observer: HistoryObserver,
        gantt_chart_wrapper_config: GanttChartWrapperConfig | None = None,
        gif_config: GifConfig | None = None,
        video_config: VideoConfig | None = None,
    ):
        """Initializes the GanttChartCreator with the given configurations
        and history observer.

        Args:
            history_observer:
                The history tracker observing the dispatcher's state.
            gantt_chart_wrapper_config:
                Configuration for the Gantt chart wrapper function. Valid keys
                are:
                - title: The title of the Gantt chart.
                - cmap: The name of the colormap to use.
                - show_available_operations: Whether to show available
                    operations in each step.

                If `title` or `cmap` are not provided here and
                `infer_gantt_chart_config` is set to True, the values from
                `gantt_chart_config` will be used if they are present.
            gif_config:
                Configuration for creating the GIF. Defaults to None.
                Valid keys are:
                - gif_path: The path to save the GIF.
                - fps: The frames per second of the GIF.
                - remove_frames: Whether to remove the frames after creating
                    the GIF.
                - frames_dir: The directory to store the frames.
                - plot_current_time: Whether to plot the current time in the
                    Gantt chart.
            video_config:
                Configuration for creating the video. Defaults to None.
                Valid keys are:
                - video_path: The path to save the video.
                - fps: The frames per second of the video.
                - remove_frames: Whether to remove the frames after creating
                    the video.
                - frames_dir: The directory to store the frames.
                - plot_current_time: Whether to plot the current time in the
                    Gantt chart.
        """
        if gif_config is None:
            gif_config = {"gif_path": None}
        if gantt_chart_wrapper_config is None:
            gantt_chart_wrapper_config = {}
        if video_config is None:
            video_config = {}

        self.gif_config = gif_config
        self.gannt_chart_wrapper_config = gantt_chart_wrapper_config
        self.video_config = video_config
        self.history_tracker = history_observer
        self.plot_function = plot_gantt_chart_wrapper(
            **self.gannt_chart_wrapper_config
        )

    @property
    def instance(self):
        """The instance being scheduled."""
        return self.history_tracker.dispatcher.instance

    @property
    def schedule(self):
        """The current schedule."""
        return self.history_tracker.dispatcher.schedule

    @property
    def dispatcher(self):
        """The dispatcher being observed."""
        return self.history_tracker.dispatcher

    def plot_gantt_chart(self) -> plt.Figure:
        """Plots the current Gantt chart of the schedule.

        Returns:
            tuple[plt.Figure, plt.Axes]:
                The figure and axes of the plotted Gantt chart.
        """
        return self.plot_function(
            self.schedule,
            None,
            self.dispatcher.available_operations(),
            self.dispatcher.current_time(),
        )

    def create_gif(self) -> None:
        """Creates a GIF of the schedule being built using the recorded
        history.

        This method uses the history of scheduled operations recorded by the
        `HistoryTracker` to create a GIF that shows the progression of the
        scheduling process.

        The GIF creation process involves:
        - Using the history of scheduled operations to generate frames for
            each step of the schedule.
        - Creating a GIF from these frames.
        - Optionally, removing the frames after the GIF is created.

        The configuration for the GIF creation can be customized through the
        `gif_config` attribute.
        """
        create_gif(
            instance=self.history_tracker.dispatcher.instance,
            schedule_history=self.history_tracker.history,
            plot_function=self.plot_function,
            **self.gif_config
        )

    def create_video(self) -> None:
        """Creates a video of the schedule being built using the recorded
        history.

        This method uses the history of scheduled operations recorded by the
        `HistoryTracker` to create a video that shows the progression of the
        scheduling process.
        """
        create_gantt_chart_video(
            instance=self.history_tracker.dispatcher.instance,
            schedule_history=self.history_tracker.history,
            plot_function=self.plot_function,
            **self.video_config
        )
