import pytest

from job_shop_lib.benchmarking import load_benchmark_instance
from job_shop_lib.dispatching import (
    Dispatcher,
    filter_non_idle_machines,
)

INSTANCES_TO_TEST = [
    load_benchmark_instance(f"la{i:02d}") for i in range(1, 11)
]


@pytest.mark.parametrize("instance", INSTANCES_TO_TEST)
def test_filter_remove_non_idle_machines(instance):
    dispatcher = Dispatcher(
        instance,
        ready_operations_filter=filter_non_idle_machines,
    )

    while not dispatcher.schedule.is_complete():
        available_operations = dispatcher.ready_operations()
        ongoing_operations = dispatcher.ongoing_operations()

        non_idle_machines = set()
        for scheduled_op in ongoing_operations:
            non_idle_machines.add(scheduled_op.machine_id)

        idle_machines = set(range(instance.num_machines)) - non_idle_machines
        for op in available_operations:
            assert any(m in idle_machines for m in op.machines)

        next_operation = available_operations[0]
        dispatcher.dispatch(next_operation, next_operation.machines[0])


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
