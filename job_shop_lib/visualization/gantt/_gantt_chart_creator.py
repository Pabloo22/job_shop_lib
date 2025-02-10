"""Home of the `GanttChartCreator` class and its configuration types."""

from typing import TypedDict, Optional
import matplotlib.pyplot as plt

from job_shop_lib.dispatching import (
    Dispatcher,
    HistoryObserver,
)
from job_shop_lib.visualization.gantt import (
    create_gantt_chart_video,
    get_partial_gantt_chart_plotter,
    create_gantt_chart_gif,
)


class PartialGanttChartPlotterConfig(TypedDict, total=False):
    """A dictionary with the configuration for creating the
    :class:`PartialGanttChartPlotter` function.

    .. seealso::

        - :class:`PartialGanttChartPlotter`
        - :func:`get_partial_gantt_chart_plotter`
    """

    title: Optional[str]
    """The title of the Gantt chart."""

    cmap: str
    """The colormap to use in the Gantt chart."""

    show_available_operations: bool
    """Whether to show available operations in each step."""


class GifConfig(TypedDict, total=False):
    """A dictionary with the configuration for creating the GIF using the
    :func:`create_gantt_chart_gif` function.

    .. seealso::

        :func:`create_gantt_chart_gif`
    """

    gif_path: Optional[str]
    """The path to save the GIF. It must end with '.gif'."""

    fps: int
    """The frames per second of the GIF. Defaults to 1."""

    remove_frames: bool
    """Whether to remove the frames after creating the GIF."""

    frames_dir: Optional[str]
    """The directory to store the frames."""

    plot_current_time: bool
    """Whether to plot the current time in the Gantt chart."""


class VideoConfig(TypedDict, total=False):
    """Configuration for creating the video using the
    :func:`create_gantt_chart_video` function.

    .. seealso::

        :func:`create_gantt_chart_video`
    """

    video_path: Optional[str]
    """The path to save the video. It must end with a valid video extension
    (e.g., '.mp4')."""

    fps: int
    """The frames per second of the video. Defaults to 1."""

    remove_frames: bool
    """Whether to remove the frames after creating the video."""

    frames_dir: Optional[str]
    """The directory to store the frames."""

    plot_current_time: bool
    """Whether to plot the current time in the Gantt chart."""


class GanttChartCreator:
    """Facade class that centralizes the creation of Gantt charts, videos
    and GIFs.

    It leverages a :class:`HistoryObserver` to keep track of the operations
    being scheduled and provides methods to plot the current state
    of the schedule as a Gantt chart and to create a GIF or video that shows
    the evolution of the schedule over time.

    It adds a new :class:`HistoryObserver` to the dispatcher if it does
    not have one already. Otherwise, it uses the observer already present.

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
            or video. Created using the :func:`get_partial_gantt_chart_plotter`
            function.

    Args:
        dispatcher:
            The :class:`Dispatcher` class that will be tracked using a
            :class:`HistoryObserver`.
        partial_gantt_chart_plotter_config:
            Configuration for the Gantt chart wrapper function through the
            :class:`PartialGanttChartPlotterConfig` class. Defaults to
            ``None``. Valid keys are:

            - title: The title of the Gantt chart.
            - cmap: The name of the colormap to use.
            - show_available_operations: Whether to show available
                operations in each step.

            If ``title`` or ``cmap`` are not provided here and
            ``infer_gantt_chart_config`` is set to ``True``, the values from
            ``gantt_chart_config`` will be used if they are present.

            .. seealso::

                - :class:`PartialGanttChartPlotterConfig`
                - :func:`get_partial_gantt_chart_plotter`
                - :class:`PartialGanttChartPlotter`

        gif_config:
            Configuration for creating the GIF. Defaults to ``None``.
            Valid keys are:

            - gif_path: The path to save the GIF.
            - fps: The frames per second of the GIF.
            - remove_frames: Whether to remove the frames after creating
                the GIF.
            - frames_dir: The directory to store the frames.
            - plot_current_time: Whether to plot the current time in the
                Gantt chart.
        video_config:
            Configuration for creating the video. Defaults to ``None``.
            Valid keys are:

            - video_path: The path to save the video.
            - fps: The frames per second of the video.
            - remove_frames: Whether to remove the frames after creating
                the video.
            - frames_dir: The directory to store the frames.
            - plot_current_time: Whether to plot the current time in the
                Gantt chart.
    """

    def __init__(
        self,
        dispatcher: Dispatcher,
        partial_gantt_chart_plotter_config: Optional[
            PartialGanttChartPlotterConfig
        ] = None,
        gif_config: Optional[GifConfig] = None,
        video_config: Optional[VideoConfig] = None,
    ):
        if gif_config is None:
            gif_config = {}
        if partial_gantt_chart_plotter_config is None:
            partial_gantt_chart_plotter_config = {}
        if video_config is None:
            video_config = {}

        self.gif_config = gif_config
        self.gannt_chart_wrapper_config = partial_gantt_chart_plotter_config
        self.video_config = video_config
        self.history_observer: HistoryObserver = (
            dispatcher.create_or_get_observer(HistoryObserver)
        )
        self.partial_gantt_chart_plotter = get_partial_gantt_chart_plotter(
            **self.gannt_chart_wrapper_config
        )

    @property
    def instance(self):
        """The instance being scheduled."""
        return self.history_observer.dispatcher.instance

    @property
    def schedule(self):
        """The current schedule."""
        return self.history_observer.dispatcher.schedule

    @property
    def dispatcher(self):
        """The dispatcher being observed."""
        return self.history_observer.dispatcher

    def plot_gantt_chart(self) -> plt.Figure:
        """Plots the current Gantt chart of the schedule.

        Returns:
            The figure of the plotted Gantt chart.
        """
        a = self.partial_gantt_chart_plotter(
            self.schedule,
            None,
            self.dispatcher.available_operations(),
            self.dispatcher.current_time(),
        )
        return a

    def create_gif(self) -> None:
        """Creates a GIF of the schedule being built using the recorded
        history.

        This method uses the history of scheduled operations recorded by the
        :class:`HistoryTracker` to create a GIF that shows the progression of
        the scheduling process.

        The GIF creation process involves:

        - Using the history of scheduled operations to generate frames for
            each step of the schedule.
        - Creating a GIF from these frames.
        - Optionally, removing the frames after the GIF is created.

        The configuration for the GIF creation can be customized through the
        ``gif_config`` attribute.
        """
        create_gantt_chart_gif(
            instance=self.history_observer.dispatcher.instance,
            schedule_history=self.history_observer.history,
            plot_function=self.partial_gantt_chart_plotter,
            **self.gif_config
        )

    def create_video(self) -> None:
        """Creates a video of the schedule being built using the recorded
        history.

        This method uses the history of scheduled operations recorded by the
        :class:`HistoryTracker` to create a video that shows the progression
        of the scheduling process.
        """
        create_gantt_chart_video(
            instance=self.history_observer.dispatcher.instance,
            schedule_history=self.history_observer.history,
            plot_function=self.partial_gantt_chart_plotter,
            **self.video_config
        )
