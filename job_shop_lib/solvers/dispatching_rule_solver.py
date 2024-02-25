from typing import Callable

from job_shop_lib import JobShopInstance, Dispatcher, Schedule, Operation
from job_shop_lib.solvers.dispatching_rules import (
    dispatching_rule_factory,
    machine_chooser_factory,
)


class DispatchingRuleSolver:
    """Solves a job shop instance using a dispatching rule algorithm."""

    def __init__(
        self,
        dispatching_rule: str | Callable[[Dispatcher], Operation] = "mwkr",
        machine_chooser: (
            str | Callable[[Dispatcher, Operation], int]
        ) = "first",
    ):
        if isinstance(dispatching_rule, str):
            dispatching_rule = dispatching_rule_factory(dispatching_rule)
        if isinstance(machine_chooser, str):
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
