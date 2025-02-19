"""Home of the `DispatchingRuleSolver` class."""

from typing import Optional, Union
from collections.abc import Callable, Iterable

from job_shop_lib import JobShopInstance, Schedule, Operation, BaseSolver
from job_shop_lib.dispatching import (
    ready_operations_filter_factory,
    Dispatcher,
    ReadyOperationsFilterType,
    ReadyOperationsFilter,
    create_composite_operation_filter,
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
        ready_operations_filter:
            The ready operations filter to use. It is used to initialize the
            dispatcher object internally when calling the solve method.

    Args:
        dispatching_rule:
            The dispatching rule to use. It can be a string with the name
            of the dispatching rule, a :class:`DispatchingRuleType` member,
            or a callable that takes a dispatcher and returns the operation to
            be dispatched next.
        machine_chooser:
            The machine chooser to use. It can be a string with the name
            of the machine chooser, a :class:`MachineChooserType` member, or a
            callable that takes a dispatcher and an operation and returns
            the machine id where the operation will be dispatched.
        ready_operations_filter:
            The ready operations filter to use. It can be either:

            - a string with the name of the pruning function
            - a :class`ReadyOperationsFilterType` enum member.
            - a callable that takes a dispatcher and a list of operations
              and returns a list of operations that should be considered
              for dispatching,
            - a list with names or actual ready operations filters to be used.
              If a list is provided, a composite filter will be created
              using the specified filters.

    .. seealso::
        - :func:`job_shop_lib.dispatching.rules.dispatching_rule_factory`
        - :func:`job_shop_lib.dispatching.rules.machine_chooser_factory`
        - :func:`~job_shop_lib.dispatching.ready_operations_filter_factory`
        - :func:`~job_shop_lib.dispatching.create_composite_operation_filter`
    """

    def __init__(
        self,
        dispatching_rule: Union[
            str, Callable[[Dispatcher], Operation]
        ] = DispatchingRuleType.MOST_WORK_REMAINING,
        machine_chooser: Union[
            str, Callable[[Dispatcher, Operation], int]
        ] = MachineChooserType.FIRST,
        ready_operations_filter: Optional[
            Union[
                Iterable[
                    Union[
                        ReadyOperationsFilter, str, ReadyOperationsFilterType
                    ]
                ],
                str,
                ReadyOperationsFilterType,
                ReadyOperationsFilter,
            ]
        ] = (
            ReadyOperationsFilterType.DOMINATED_OPERATIONS,
            ReadyOperationsFilterType.NON_IMMEDIATE_OPERATIONS,
        ),
    ):
        if isinstance(dispatching_rule, str):
            dispatching_rule = dispatching_rule_factory(dispatching_rule)
        if isinstance(machine_chooser, str):
            machine_chooser = machine_chooser_factory(machine_chooser)
        if isinstance(ready_operations_filter, str):
            ready_operations_filter = ready_operations_filter_factory(
                ready_operations_filter
            )
        if isinstance(ready_operations_filter, Iterable):
            ready_operations_filter = create_composite_operation_filter(
                ready_operations_filter
            )

        self.dispatching_rule = dispatching_rule
        self.machine_chooser = machine_chooser
        self.ready_operations_filter = ready_operations_filter

    def solve(
        self,
        instance: JobShopInstance,
        dispatcher: Optional[Dispatcher] = None,
    ) -> Schedule:
        """Solves the instance using the dispatching rule and machine chooser
        algorithms.

        Args:
            instance:
                The job shop instance to be solved.
            dispatcher:
                The dispatcher object that will be used to dispatch the
                operations. If not provided, a new dispatcher will be created
                using the ready operations filter provided in the constructor.

        Returns:
            The schedule obtained after solving the instance.

        .. tip::
            Another way to use the solver is by calling it as a function. This
            will call the ``solve`` method internally and will add metadata to
            the schedule. For example:

            .. code-block:: python

                solver = DispatchingRuleSolver()
                schedule = solver(instance)
        """
        if dispatcher is None:
            dispatcher = Dispatcher(
                instance, ready_operations_filter=self.ready_operations_filter
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
    # import pstats
    # from io import StringIO
    from job_shop_lib.benchmarking import (
        # load_benchmark_instance,
        load_all_benchmark_instances,
    )

    # from job_shop_lib.dispatching.rules._dispatching_rules_functions import (
    #     most_work_remaining_rule_2,
    # )

    # ta_instances = [
    #     load_benchmark_instance(f"ta{i:02d}") for i in range(1, 81)
    # ]
    ta_instances = load_all_benchmark_instances().values()
    solver = DispatchingRuleSolver(
        dispatching_rule="most_work_remaining", ready_operations_filter=None
    )

    start = time.perf_counter()

    # Create a Profile object
    profiler = cProfile.Profile()

    # Run the code under profiling
    # profiler.enable()
    for instance_ in ta_instances:
        solver.solve(instance_)
    # profiler.disable()

    end = time.perf_counter()

    # Print elapsed time
    print(f"Elapsed time: {end - start:.2f} seconds.")

    # Print profiling results
    # s = StringIO()
    # ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    # profiler.print_stats("cumtime")  # Print top 20 time-consuming functions
    # print(s.getvalue())
