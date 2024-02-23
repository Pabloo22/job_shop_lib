import os
import pathlib
import shutil
from typing import Optional

import imageio
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from job_shop_lib import JobShopInstance, Dispatcher
from job_shop_lib.solvers import DispatchingRuleSolver
from job_shop_lib.visualization import plot_gantt_chart


def create_gif_from_dispatching_rule_solver(
    instance: JobShopInstance,
    solver: DispatchingRuleSolver,
    gif_path: str,
    fps: int = 1,
    remove_frames: bool = True,
    gantt_charts_title: Optional[str] = None,
    gantt_charts_cmap: str = "viridis",
) -> None:
    frames_dir = _create_directory_for_frames("frames")
    _create_gantt_chart_frames(
        instance, solver, frames_dir, gantt_charts_title, gantt_charts_cmap
    )
    _create_gif_from_frames(frames_dir, gif_path, fps)

    if remove_frames:
        shutil.rmtree(frames_dir)


def _create_directory_for_frames(dir_name: str) -> str:
    path = pathlib.Path(dir_name)
    path.mkdir(exist_ok=True)
    return str(path)


def _create_gif_from_frames(frames_dir: str, gif_path: str, fps: int) -> None:
    frames = [
        os.path.join(frames_dir, frame) for frame in os.listdir(frames_dir)
    ]
    images = [imageio.imread(frame) for frame in frames]
    imageio.mimsave(gif_path, images, fps=fps)


def _create_gantt_chart_frames(
    instance: JobShopInstance,
    solver: DispatchingRuleSolver,
    frames_dir: str,
    gantt_charts_title: Optional[str],
    gantt_charts_cmap: str,
) -> None:
    makespan = solver(instance).makespan()
    dispatcher = Dispatcher(instance)
    schedule = dispatcher.schedule
    iteration = 0

    fig, _ = plot_gantt_chart(schedule, xlim=makespan)
    _save_frame(fig, frames_dir, iteration)

    while not schedule.is_complete():
        solver.step(dispatcher)
        iteration += 1
        fig, _ = plot_gantt_chart(
            schedule, gantt_charts_title, gantt_charts_cmap
        )
        _save_frame(fig, frames_dir, iteration)


def _save_frame(figure: Figure, frames_dir: str, number: int) -> None:
    figure.savefig(f"{frames_dir}/frame_{number:02d}.png")
    plt.close(figure)
