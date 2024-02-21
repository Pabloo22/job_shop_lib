from typing import Optional
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Patch

from job_shop_lib import ScheduledOperation, JobShopInstance


class Schedule:
    __slots__ = ("instance", "schedule", "metadata")

    def __init__(
        self,
        instance: JobShopInstance,
        schedule: Optional[list[list[ScheduledOperation]]] = None,
        **metadata,
    ):
        if schedule is None:
            schedule = [[] for _ in range(instance.num_machines)]

        Schedule.check_schedule(schedule)

        self.instance = instance
        self.schedule = schedule
        self.metadata = metadata

    def reset(self):
        self.schedule = [[] for _ in range(self.instance.num_machines)]

    def makespan(self) -> int:
        max_end_time = 0
        for machine_schedule in self.schedule:
            if machine_schedule:
                max_end_time = max(max_end_time, machine_schedule[-1].end_time)
        return max_end_time

    def is_complete(self) -> bool:
        num_scheduled_operations = sum(
            len(machine_schedule) for machine_schedule in self.schedule
        )
        return num_scheduled_operations == self.instance.num_operations

    def add(self, scheduled_operation: ScheduledOperation):
        self._check_start_time_of_new_operation(scheduled_operation)
        self.schedule[scheduled_operation.machine_id].append(
            scheduled_operation
        )

    def _check_start_time_of_new_operation(
        self,
        new_operation: ScheduledOperation,
    ):
        is_first_operation = not self.schedule[new_operation.machine_id]
        if is_first_operation:
            return

        last_operation = self.schedule[new_operation.machine_id][-1]
        self._check_start_time(new_operation, last_operation)

    @staticmethod
    def check_schedule(schedule: list[list[ScheduledOperation]]):
        for machine_id, scheduled_operations in enumerate(schedule):
            for i, scheduled_operation in enumerate(scheduled_operations):
                if scheduled_operation.machine_id != machine_id:
                    raise ValueError(
                        "The machine id of the scheduled operation "
                        f"({ScheduledOperation.machine_id}) does not match "
                        f"the machine id of the machine schedule ({machine_id}"
                        f"). Index of the operation: [{machine_id}][{i}]."
                    )

                if i == 0:
                    continue

                Schedule._check_start_time(
                    scheduled_operation, scheduled_operations[i - 1]
                )

    @staticmethod
    def _check_start_time(
        scheduled_operation: ScheduledOperation,
        previous_operation: ScheduledOperation,
    ):
        """Raises a ValueError if the start time of the new operation is before
        the end time of the last operation on the same machine."""

        if previous_operation.end_time <= scheduled_operation.start_time:
            return

        raise ValueError(
            "Operation cannot be scheduled before the last operation on "
            "the same machine: end time of last operation "
            f"({previous_operation.end_time}) > start time of new operation "
            f"({scheduled_operation.start_time})."
        )

    def __repr__(self) -> str:
        return str(self.schedule)

    def plot_gantt_chart(
        self, title: Optional[str] = None, cmap_name: str = "viridis"
    ) -> tuple[Figure, plt.Axes]:
        """Plots a Gantt chart for the schedule."""
        fig, ax = self._initialize_plot(title)
        legend_handles = self._plot_machine_schedules(ax, cmap_name)
        self._configure_legend(ax, legend_handles)
        self._configure_axes(ax)
        return fig, ax

    def _initialize_plot(
        self, title: Optional[str]
    ) -> tuple[Figure, plt.Axes]:
        """Initializes the plot."""
        fig, ax = plt.subplots()
        ax.set_xlabel("Time units")
        ax.set_ylabel("Machines")
        ax.grid(True, which="both", axis="x", linestyle="--", linewidth=0.5)
        ax.yaxis.grid(False)
        if title is None:
            title = f"Gantt Chart for {self.instance.name} instance"
        plt.title(title)
        return fig, ax

    def _plot_machine_schedules(
        self, ax: plt.Axes, cmap_name: str
    ) -> dict[int, Patch]:
        """Plots the schedules for each machine."""
        max_job_id = self.instance.num_jobs - 1
        cmap = plt.cm.get_cmap(cmap_name, max_job_id + 1)
        norm = Normalize(vmin=0, vmax=max_job_id)
        legend_handles = {}

        for machine_index, machine_schedule in enumerate(self.schedule):
            y_position_for_machines = 10 + 10 * machine_index

            for scheduled_op in machine_schedule:
                color = cmap(norm(scheduled_op.job_id))
                self._plot_scheduled_operation(
                    ax, scheduled_op, y_position_for_machines, color
                )
                if scheduled_op.job_id not in legend_handles:
                    legend_handles[scheduled_op.job_id] = Patch(
                        facecolor=color, label=f"Job {scheduled_op.job_id + 1}"
                    )

        return legend_handles

    def _plot_scheduled_operation(
        self, ax: plt.Axes, scheduled_op, y_position_for_machines: int, color
    ):
        """Plots a single scheduled operation."""
        start_time, end_time = scheduled_op.start_time, scheduled_op.end_time
        duration = end_time - start_time
        ax.broken_barh(
            [(start_time, duration)],
            (y_position_for_machines, 9),
            facecolors=color,
        )

    def _configure_legend(self, ax: plt.Axes, legend_handles: dict[int, Patch]):
        """Configures the legend for the plot."""
        sorted_legend_handles = [
            legend_handles[job_id] for job_id in sorted(legend_handles)
        ]
        ax.legend(handles=sorted_legend_handles, loc="lower right")

    def _configure_axes(self, ax: plt.Axes):
        """Sets the limits and labels for the axes."""
        num_machines = len(self.schedule)
        ax.set_ylim(0, 10 + 10 * num_machines)
        ax.set_yticks([15 + 10 * i for i in range(num_machines)])
        ax.set_yticklabels([str(i + 1) for i in range(num_machines)])
        ax.set_xlim(0, self.makespan() + 1)
