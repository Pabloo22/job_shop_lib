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

        self._check_initialization(schedule)

        self.instance = instance
        self.schedule = schedule
        self.metadata = metadata

    def makespan(self) -> int:
        return max(
            scheduled_operation.end_time
            for machine_schedule in self.schedule
            for scheduled_operation in machine_schedule
        )

    def is_complete(self) -> bool:
        num_scheduled_operations = sum(
            len(machine_schedule) for machine_schedule in self.schedule
        )
        return num_scheduled_operations == self.instance.num_operations

    def is_empty(self) -> bool:
        return all(not machine_schedule for machine_schedule in self.schedule)

    def dispatch(self, scheduled_operation: ScheduledOperation):
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

    def _check_initialization(self, schedule: list[list[ScheduledOperation]]):
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

                self._check_start_time(
                    scheduled_operation, scheduled_operations[i - 1]
                )

    def _check_start_time(
        self,
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
        """Plots a Gantt chart for the schedule.

        We return the figure so that the user can save the chart to a file,
        or add additional elements to the chart.

        Args:
            title (Optional[str], optional): Title of the chart. Defaults to
                "Gantt Chart for {self.instance.name} instance". To disable the
                title, pass an empty string.
            cmap_name (str, optional): Name of the colormap. Defaults to
                "viridis".

        Returns:
            Figure: Matplotlib figure. We return the figure so that the user
                can save the chart to a file, or add additional elements to the
                chart.
            Axes: Matplotlib axes.
        """
        fig, ax = plt.subplots()

        ax.set_xlabel("Time units")
        ax.set_ylabel("Machines")

        ax.grid(True, which="both", axis="x", linestyle="--", linewidth=0.5)
        ax.yaxis.grid(False)

        max_job_id = self.instance.num_jobs - 1
        cmap = plt.cm.get_cmap(cmap_name, max_job_id + 1)
        norm = Normalize(vmin=0, vmax=max_job_id)

        legend_handles = {}
        for machine_index, machine_schedule in enumerate(self.schedule):
            y_position_for_machines = 10 + 10 * machine_index

            for scheduled_op in machine_schedule:
                start_time = scheduled_op.start_time
                end_time = scheduled_op.end_time
                job_id = scheduled_op.job_id
                duration = end_time - start_time
                color = cmap(norm(job_id))
                ax.broken_barh(
                    [(start_time, duration)],
                    (y_position_for_machines, 9),
                    facecolors=color,
                )

                if job_id not in legend_handles:
                    legend_handles[job_id] = Patch(
                        facecolor=color, label=f"Job {job_id + 1}"
                    )

        sorted_legend_handles = [
            legend_handles[job_id] for job_id in sorted(legend_handles)
        ]

        num_machines = len(self.schedule)
        ax.set_ylim(0, 10 + 10 * num_machines)
        ax.set_yticks([15 + 10 * i for i in range(num_machines)])
        ax.set_yticklabels([str(i + 1) for i in range(num_machines)])

        ax.set_xlim(0, self.makespan() + 1)

        if title is None:
            title = f"Gantt Chart for {self.instance.name} instance"
        plt.title(title)
        plt.legend(handles=sorted_legend_handles)

        return fig, ax
