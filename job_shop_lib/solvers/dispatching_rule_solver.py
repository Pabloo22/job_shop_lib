from typing import Callable

from job_shop_lib import JobShopInstance, Dispatcher, Schedule, Operation
from job_shop_lib.solvers import (
    Solver,
    dispatching_rule_factory,
    machine_chooser_factory,
    DispatchingRule,
    MachineChooser,
)


class DispatchingRuleSolver(Solver):
    """Solves a job shop instance using a dispatching rule algorithm."""

    def __init__(
        self,
        dispatching_rule: (
            DispatchingRule | str | Callable[[Dispatcher], Operation]
        ) = DispatchingRule.MOST_WORK_REMAINING,
        machine_chooser: (
            DispatchingRule | str | Callable[[Dispatcher, Operation], int]
        ) = MachineChooser.FIRST,
    ):
        if isinstance(dispatching_rule, str | DispatchingRule):
            dispatching_rule = dispatching_rule_factory(dispatching_rule)
        if isinstance(machine_chooser, str | MachineChooser):
            machine_chooser = machine_chooser_factory(machine_chooser)
        self.dispatching_rule = dispatching_rule
        self.machine_chooser = machine_chooser

    def solve(self, instance: JobShopInstance) -> Schedule:
        dispatcher = Dispatcher(instance)
        while not dispatcher.schedule.is_complete():
            self.step(dispatcher)

        return dispatcher.schedule

    def step(self, dispatcher: Dispatcher) -> None:
        selected_operation = self.dispatching_rule(dispatcher)
        machine_id = self.machine_chooser(dispatcher, selected_operation)
        dispatcher.dispatch(selected_operation, machine_id)

    def __call__(self, instance: JobShopInstance) -> Schedule:
        return self.solve(instance)
