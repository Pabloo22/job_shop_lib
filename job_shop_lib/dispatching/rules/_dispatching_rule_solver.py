"""Home of the `DispatchingRuleSolver` class."""

from collections.abc import Callable

from job_shop_lib import JobShopInstance, Schedule, Operation, BaseSolver
from job_shop_lib.dispatching import (
    ready_operations_filter_factory,
    Dispatcher,
    ReadyOperationsFilterType,
)
from job_shop_lib.dispatching.rules import (
    dispatching_rule_factory,
    machine_chooser_factory,
    DispatchingRuleType,
    MachineChooserType,
)


class DispatchingRuleSolver(BaseSolver):
    """Solves a job shop instance using a dispatching rule.

    Attributes:
        dispatching_rule:
            The dispatching rule to use. It is a callable that takes a
            dispatcher and returns the operation to be dispatched next.
        machine_chooser:
            Used to choose the machine where the operation will be dispatched
            to. It is only used if the operation can be dispatched to multiple
            machines.
        pruning_function:
            The pruning function to use. It is used to initialize the
            dispatcher object internally when calling the solve method.
    """

    def __init__(
        self,
        dispatching_rule: (
            str | Callable[[Dispatcher], Operation]
        ) = DispatchingRuleType.MOST_WORK_REMAINING,
        machine_chooser: (
            str | Callable[[Dispatcher, Operation], int]
        ) = MachineChooserType.FIRST,
        pruning_function: (
            str
            | Callable[[Dispatcher, list[Operation]], list[Operation]]
            | None
        ) = ReadyOperationsFilterType.DOMINATED_OPERATIONS,
    ):
        """Initializes the solver with the given dispatching rule, machine
        chooser and pruning function.

        Args:
            dispatching_rule:
                The dispatching rule to use. It can be a string with the name
                of the dispatching rule, a DispatchingRule enum member, or a
                callable that takes a dispatcher and returns the operation to
                be dispatched next.
            machine_chooser:
                The machine chooser to use. It can be a string with the name
                of the machine chooser, a MachineChooser enum member, or a
                callable that takes a dispatcher and an operation and returns
                the machine id where the operation will be dispatched.
            pruning_function:
                The pruning function to use. It can be a string with the name
                of the pruning function, a PruningFunction enum member, or a
                callable that takes a dispatcher and a list of operations and
                returns a list of operations that should be considered for
                dispatching.
        """
        if isinstance(dispatching_rule, str):
            dispatching_rule = dispatching_rule_factory(dispatching_rule)
        if isinstance(machine_chooser, str):
            machine_chooser = machine_chooser_factory(machine_chooser)
        if isinstance(pruning_function, str):
            pruning_function = ready_operations_filter_factory(
                pruning_function
            )

        self.dispatching_rule = dispatching_rule
        self.machine_chooser = machine_chooser
        self.pruning_function = pruning_function

    def solve(
        self, instance: JobShopInstance, dispatcher: Dispatcher | None = None
    ) -> Schedule:
        """Returns a schedule for the given job shop instance using the
        dispatching rule algorithm."""
        if dispatcher is None:
            dispatcher = Dispatcher(
                instance, ready_operations_filter=self.pruning_function
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
    import time
    import cProfile
    import pstats
    from io import StringIO
    from job_shop_lib.benchmarking import load_benchmark_instance

    # from job_shop_lib.dispatching.rules._dispatching_rules_functions import (
    #     most_work_remaining_rule_2,
    # )

    ta_instances = [
        load_benchmark_instance(f"ta{i:02d}") for i in range(1, 81)
    ]
    solver = DispatchingRuleSolver(
        dispatching_rule="most_work_remaining", pruning_function=None
    )

    start = time.perf_counter()

    # Create a Profile object
    profiler = cProfile.Profile()

    # Run the code under profiling
    profiler.enable()
    for instance_ in ta_instances:
        solver.solve(instance_)
    profiler.disable()

    end = time.perf_counter()

    # Print elapsed time
    print(f"Elapsed time: {end - start:.2f} seconds.")

    # Print profiling results
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    profiler.print_stats("cumtime")  # Print top 20 time-consuming functions
    # print(s.getvalue())
