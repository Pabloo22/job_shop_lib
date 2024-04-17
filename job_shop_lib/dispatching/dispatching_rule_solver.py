from collections.abc import Callable

from job_shop_lib import JobShopInstance, Schedule, Operation, BaseSolver
from job_shop_lib.dispatching import (
    dispatching_rule_factory,
    machine_chooser_factory,
    pruning_function_factory,
    DispatchingRule,
    MachineChooser,
    Dispatcher,
    PruningFunction,
)


class DispatchingRuleSolver(BaseSolver):
    """Solves a job shop instance using a dispatching rule algorithm."""

    def __init__(
        self,
        dispatching_rule: (
            str | Callable[[Dispatcher], Operation]
        ) = DispatchingRule.MOST_WORK_REMAINING,
        machine_chooser: (
            str | Callable[[Dispatcher, Operation], int]
        ) = MachineChooser.FIRST,
        pruning_function: (
            str
            | Callable[[Dispatcher, list[Operation]], list[Operation]]
            | None
        ) = PruningFunction.DOMINATED_OPERATIONS,
    ):
        if isinstance(dispatching_rule, str):
            dispatching_rule = dispatching_rule_factory(dispatching_rule)
        if isinstance(machine_chooser, str):
            machine_chooser = machine_chooser_factory(machine_chooser)
        if isinstance(pruning_function, str):
            pruning_function = pruning_function_factory(pruning_function)

        self.dispatching_rule = dispatching_rule
        self.machine_chooser = machine_chooser
        self.pruning_function = pruning_function

    def solve(self, instance: JobShopInstance) -> Schedule:
        """Returns a schedule for the given job shop instance using the
        dispatching rule algorithm."""
        dispatcher = Dispatcher(
            instance, pruning_function=self.pruning_function
        )
        while not dispatcher.schedule.is_complete():
            self.step(dispatcher)

        return dispatcher.schedule

    def step(self, dispatcher: Dispatcher) -> None:
        """Executes one step of the dispatching rule algorithm.

        Args:
            dispatcher:
                The dispatcher object that will be used to dispatch the
                operations.
        """
        selected_operation = self.dispatching_rule(dispatcher)
        machine_id = self.machine_chooser(dispatcher, selected_operation)
        dispatcher.dispatch(selected_operation, machine_id)


if __name__ == "__main__":
    import cProfile
    from job_shop_lib.benchmarking import load_benchmark_instance

    ta_instances = []
    for i in range(1, 81):
        ta_instances.append(load_benchmark_instance(f"ta{i:02d}"))
    solver = DispatchingRuleSolver(dispatching_rule="most_work_remaining")
    cProfile.run("for instance in ta_instances: solver.solve(instance)")
