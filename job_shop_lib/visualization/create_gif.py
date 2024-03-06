import os
import pathlib
import shutil
from typing import Optional, Callable

import imageio
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from job_shop_lib import JobShopInstance, Dispatcher, Schedule
from job_shop_lib.solvers import DispatchingRuleSolver
from job_shop_lib.visualization.gantt_chart import plot_gantt_chart


def create_gif(
    gif_path: str,
    instance: JobShopInstance,
    solver: DispatchingRuleSolver,
    plot_function: Optional[Callable[[Schedule, int], Figure]] = None,
    fps: int = 1,
    remove_frames: bool = True,
) -> None:
    if plot_function is None:
        plot_function = get_default_plot_function()

    path = pathlib.Path("temp_frames")
    path.mkdir(exist_ok=True)
    frames_dir = str(path)
    create_gantt_chart_frames(frames_dir, instance, solver, plot_function)
    create_gif_from_frames(frames_dir, gif_path, fps)

    if remove_frames:
        shutil.rmtree(frames_dir)


def get_default_plot_function(
    title: Optional[str] = None, cmap: str = "viridis"
) -> Callable[[Schedule, int], Figure]:
    def default_plot_function(schedule: Schedule, makespan: int) -> Figure:
        fig, _ = plot_gantt_chart(
            schedule, title=title, cmap_name=cmap, xlim=makespan
        )
        return fig

    return default_plot_function


def create_gantt_chart_frames(
    frames_dir: str,
    instance: JobShopInstance,
    solver: DispatchingRuleSolver,
    plot_function: Callable[[Schedule, int], Figure],
) -> None:
    dispatcher = Dispatcher(instance)
    schedule = dispatcher.schedule
    makespan = solver(instance).makespan()
    iteration = 0

    while not schedule.is_complete():
        solver.step(dispatcher)
        iteration += 1
        fig = plot_function(schedule, makespan)
        _save_frame(fig, frames_dir, iteration)


def _save_frame(figure: Figure, frames_dir: str, number: int) -> None:
    figure.savefig(f"{frames_dir}/frame_{number:02d}.png", bbox_inches="tight")
    plt.close(figure)


def create_gif_from_frames(frames_dir: str, gif_path: str, fps: int) -> None:
    frames = [
        os.path.join(frames_dir, frame)
        for frame in sorted(os.listdir(frames_dir))
    ]
    images = [imageio.imread(frame) for frame in frames]
    imageio.mimsave(gif_path, images, fps=fps)
