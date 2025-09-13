import pytest
import numpy as np
from numpy.typing import NDArray

from job_shop_lib.exceptions import ValidationError
from job_shop_lib import Operation, JobShopInstance, ScheduledOperation
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.reinforcement_learning import (
    add_padding,
    create_edge_type_dict,
    map_values,
    get_optimal_actions,
    get_deadline_violation_penalty,
    get_due_date_violation_penalty,
)
from job_shop_lib.dispatching import OptimalOperationsObserver
from job_shop_lib.dispatching.rules import DispatchingRuleSolver


def test_add_padding_int_array():
    array = np.array(
        [
            [1, 2],
            [3, 4],
        ],
        dtype=np.int32,
    )
    output_shape = (3, 3)
    result: NDArray[np.int32] = add_padding(array, output_shape)
    expected = np.array(
        [
            [1, 2, -1],
            [3, 4, -1],
            [-1, -1, -1],
        ],
    )
    assert np.array_equal(result, expected)


def test_add_padding_float_array():
    array = np.array(
        [
            [1.0, 2.0],
            [3.0, 4.0],
        ],
        dtype=np.float32,
    )
    output_shape = (3, 3)
    result: NDArray[np.float32] = add_padding(array, output_shape)
    expected = np.array(
        [
            [1.0, 2.0, -1.0],
            [3.0, 4.0, -1.0],
            [-1.0, -1.0, -1.0],
        ],
    )
    assert np.array_equal(result, expected)


def test_add_padding_bool_array():
    array = np.array(
        [
            [True, False],
            [False, True],
        ],
        dtype=bool,
    )
    output_shape = (3, 3)
    result: NDArray[np.bool_] = add_padding(
        array, output_shape, padding_value=False
    )
    expected = np.array(
        [
            [True, False, False],
            [False, True, False],
            [False, False, False],
        ],
    )
    assert np.array_equal(result, expected)


def test_add_padding_int_array_with_padding_value():
    array = np.array(
        [
            [1, 2],
            [3, 4],
        ],
        dtype=np.int32,
    )
    output_shape = (3, 3)
    padding_value = 0
    result: NDArray[np.int32] = add_padding(array, output_shape, padding_value)
    expected = np.array(
        [
            [1, 2, 0],
            [3, 4, 0],
            [0, 0, 0],
        ],
    )
    assert np.array_equal(result, expected)


def test_add_padding_bool_array_with_dtype():
    array = np.array(
        [
            [True, False],
            [False, True],
        ],
        dtype=bool,
    )
    output_shape = (3, 3)
    result = add_padding(array, output_shape, dtype=np.int32)
    expected = np.array(
        [
            [1, 0, -1],
            [0, 1, -1],
            [-1, -1, -1],
        ],
    )
    assert np.array_equal(result, expected)


def test_add_padding_raises_error():
    array = np.array(
        [
            [1, 2],
            [3, 4],
        ],
        dtype=np.int32,
    )
    output_shape = (1, 3)
    with pytest.raises(ValidationError):
        add_padding(array, output_shape)


def test_basic_bipartite():
    """Test basic bipartite graph with two node types."""
    edge_index = np.array(
        [
            [0, 0, 1, 1],  # source nodes
            [2, 3, 2, 3],  # target nodes
        ]
    )

    type_ranges = {"user": (0, 2), "item": (2, 4)}

    result = create_edge_type_dict(edge_index, type_ranges)

    # Check all possible type combinations
    assert ("user", "to", "item") in result
    assert np.array_equal(result[("user", "to", "item")], edge_index)

    # These combinations should be empty
    assert result[("user", "to", "user")].size == 0
    assert result[("item", "to", "item")].size == 0
    assert result[("item", "to", "user")].size == 0


def test_three_node_types():
    """Test graph with three node types."""
    edge_index = np.array(
        [
            [0, 1, 2, 3, 4],  # source nodes
            [3, 3, 5, 5, 5],  # target nodes
        ]
    )

    type_ranges = {
        "user": (0, 2),  # nodes 0,1
        "item": (2, 4),  # nodes 2,3
        "category": (4, 6),  # nodes 4,5
    }

    result = create_edge_type_dict(edge_index, type_ranges)

    # Test user to item edges
    user_to_item = result[("user", "to", "item")]
    assert np.array_equal(user_to_item, np.array([[0, 1], [3, 3]]))

    # Test item to category edges
    item_to_category = result[("item", "to", "category")]
    assert np.array_equal(item_to_category, np.array([[2, 3], [5, 5]]))

    # Test category to category edges
    category_to_category = result[("category", "to", "category")]
    assert np.array_equal(category_to_category, np.array([[4], [5]]))

    # Verify that non-existent edges have empty arrays
    assert result[("user", "to", "user")].size == 0
    assert result[("user", "to", "category")].size == 0
    assert result[("category", "to", "user")].size == 0
    assert result[("category", "to", "item")].size == 0
    assert result[("item", "to", "user")].size == 0
    assert result[("item", "to", "item")].size == 0


def test_zeros_edge_index():
    """Test with empty edge index."""
    edge_index = np.zeros((2, 0))

    type_ranges = {"user": (0, 2), "item": (2, 4), "category": (4, 6)}

    result = create_edge_type_dict(edge_index, type_ranges)

    user_to_user = result[("user", "to", "user")]
    assert len(result) == 9
    assert np.array_equal(user_to_user, edge_index)


def test_single_node_type():
    """Test with single node type."""
    edge_index = np.array([[0, 1, 1, 2], [1, 0, 2, 1]])

    type_ranges = {"user": (0, 3)}

    result = create_edge_type_dict(edge_index, type_ranges)

    assert ("user", "to", "user") in result
    assert np.array_equal(result[("user", "to", "user")], edge_index)


def test_out_of_range_edges():
    """Test handling of edges that are out of the specified ranges."""
    edge_index = np.array(
        [
            [0, 1, 5, 2],  # node 5 is out of range
            [1, 2, 1, 5],  # node 5 is out of range
        ]
    )

    type_ranges = {"user": (0, 2), "item": (2, 4)}

    result = create_edge_type_dict(edge_index, type_ranges)

    # Check that out-of-range edges are not included
    user_to_user = result[("user", "to", "user")]
    assert user_to_user.shape[1] == 1  # Only one valid user-to-user edge
    assert np.array_equal(user_to_user, np.array([[0], [1]]))


def test_edge_case_adjacent_ranges():
    """Test with adjacent ranges."""
    edge_index = np.array([[1, 2, 3], [2, 3, 4]])

    type_ranges = {"type1": (0, 2), "type2": (2, 4), "type3": (4, 6)}

    result = create_edge_type_dict(edge_index, type_ranges)

    # Check edges at the boundaries
    assert np.array_equal(
        result[("type1", "to", "type2")], np.array([[1], [2]])
    )


def test_basic_sequential_mapping():
    edge_index = np.array(
        [
            [0, 1, 2],
            [1, 2, 0],
        ]
    )
    mapping = {0: 0, 1: 1, 2: 2}
    result = map_values(edge_index, mapping)
    expected = np.array([[0, 1, 2], [1, 2, 0]])
    np.testing.assert_array_equal(result, expected)


def test_non_sequential_global_ids():
    edge_index = np.array([[10, 20], [20, 30]]).reshape(2, -1)
    mapping = {10: 0, 20: 1, 30: 2}
    result = map_values(edge_index, mapping)
    expected = np.array([[0, 1], [1, 2]]).reshape(2, -1)
    np.testing.assert_array_equal(result, expected)


def test_empty_edge_index():
    edge_index = np.array([], dtype=int).reshape(2, 0)
    mapping = {0: 0, 1: 1}
    result = map_values(edge_index, mapping)
    expected = np.array([], dtype=int).reshape(2, 0)
    np.testing.assert_array_equal(result, expected)


def test_single_edge():
    edge_index = np.array([[5], [10]])
    mapping = {5: 0, 10: 1}
    result = map_values(edge_index, mapping)
    expected = np.array([[0], [1]]).reshape(2, -1)
    np.testing.assert_array_equal(result, expected)


def test_repeated_nodes():
    edge_index = np.array([[1, 1, 2], [2, 3, 3]])
    mapping = {1: 0, 2: 1, 3: 2, 4: 5}
    result = map_values(edge_index, mapping)
    expected = np.array([[0, 0, 1], [1, 2, 2]])
    np.testing.assert_array_equal(result, expected)


def test_invalid_global_id():
    edge_index = np.array([[0, 1], [1, 2]])
    mapping = {0: 0, 1: 1}  # Missing mapping for 2
    with pytest.raises(ValidationError):
        map_values(edge_index, mapping)


def _make_scheduled_operation(
    *,
    duration: int,
    start_time: int,
    machine: int = 0,
    deadline=None,
    due_date=None,
):
    """Helper to build a minimal scheduled operation and dispatcher."""
    jobs = [
        [
            Operation(
                machine,
                duration=duration,
                deadline=deadline,
                due_date=due_date,
            )
        ]
    ]
    instance = JobShopInstance(jobs, name="PenaltyTestInstance")
    dispatcher = Dispatcher(instance)
    op = instance.jobs[0][0]
    scheduled_op = ScheduledOperation(
        op, start_time=start_time, machine_id=machine
    )
    return scheduled_op, dispatcher


# ---------------- Deadline penalty tests ---------------- #


def test_deadline_penalty_violation():
    scheduled_op, dispatcher = _make_scheduled_operation(
        duration=10, start_time=0, deadline=5
    )  # end_time = 10 > 5
    assert get_deadline_violation_penalty(scheduled_op, dispatcher) == 10_000


def test_deadline_penalty_no_violation_equal_boundary():
    scheduled_op, dispatcher = _make_scheduled_operation(
        duration=5, start_time=0, deadline=5
    )  # end_time = 5 == 5
    assert get_deadline_violation_penalty(scheduled_op, dispatcher) == 0.0


def test_deadline_penalty_none_deadline():
    scheduled_op, dispatcher = _make_scheduled_operation(
        duration=4, start_time=0, deadline=None
    )
    assert get_deadline_violation_penalty(scheduled_op, dispatcher) == 0.0


def test_deadline_penalty_custom_factor():
    scheduled_op, dispatcher = _make_scheduled_operation(
        duration=3, start_time=0, deadline=2
    )  # end_time = 3 > 2
    assert (
        get_deadline_violation_penalty(
            scheduled_op, dispatcher, deadline_penalty_factor=123.45
        )
        == 123.45
    )


# ---------------- Due date penalty tests ---------------- #


def test_due_date_penalty_violation():
    scheduled_op, dispatcher = _make_scheduled_operation(
        duration=7, start_time=0, due_date=6
    )  # end_time = 7 > 6
    assert get_due_date_violation_penalty(scheduled_op, dispatcher) == 100


def test_due_date_penalty_no_violation_equal_boundary():
    scheduled_op, dispatcher = _make_scheduled_operation(
        duration=5, start_time=0, due_date=5
    )  # end_time = 5 == 5
    assert get_due_date_violation_penalty(scheduled_op, dispatcher) == 0.0


def test_due_date_penalty_none_due_date():
    scheduled_op, dispatcher = _make_scheduled_operation(
        duration=4, start_time=0, due_date=None
    )
    assert get_due_date_violation_penalty(scheduled_op, dispatcher) == 0.0


def test_due_date_penalty_custom_factor():
    scheduled_op, dispatcher = _make_scheduled_operation(
        duration=9, start_time=0, due_date=1
    )  # end_time = 9 > 1
    assert (
        get_due_date_violation_penalty(
            scheduled_op, dispatcher, due_date_penalty_factor=7.5
        )
        == 7.5
    )


# ---------------- get_optimal_actions tests ---------------- #


def test_get_optimal_actions_initial_and_after_step(
    example_job_shop_instance: JobShopInstance,
):
    # Build a reference schedule using a simple heuristic solver
    solver = DispatchingRuleSolver()
    reference_schedule = solver.solve(example_job_shop_instance)

    # Fresh dispatcher and observer on same instance
    dispatcher = Dispatcher(example_job_shop_instance)
    optimal_obs = OptimalOperationsObserver(dispatcher, reference_schedule)

    # Build available actions tuples (operation_id, machine_id, job_id)
    available_ops = dispatcher.available_operations()
    actions = [
        (op.operation_id, op.machine_id, op.job_id) for op in available_ops
    ]

    # Compute mapping and expected optimal ids
    mapping = get_optimal_actions(optimal_obs, actions)
    expected_ones = {
        (op.operation_id, op.machine_id, op.job_id)
        for op in optimal_obs.optimal_available
    }

    # Check 1 for optimal, 0 otherwise
    for a in actions:
        assert mapping[a] == int(a in expected_ones)

    # Dispatch one optimal operation and validate mapping updates
    op_to_dispatch = next(iter(optimal_obs.optimal_available))
    dispatcher.dispatch(op_to_dispatch)

    available_ops = dispatcher.available_operations()
    actions = [
        (op.operation_id, op.machine_id, op.job_id) for op in available_ops
    ]
    mapping = get_optimal_actions(optimal_obs, actions)
    expected_ones = {
        (op.operation_id, op.machine_id, op.job_id)
        for op in optimal_obs.optimal_available
    }
    for a in actions:
        assert mapping[a] == int(a in expected_ones)


def test_get_optimal_actions_marks_non_optimal_zero(
    example_job_shop_instance: JobShopInstance,
):
    solver = DispatchingRuleSolver()
    reference_schedule = solver.solve(example_job_shop_instance)
    dispatcher = Dispatcher(example_job_shop_instance)
    optimal_obs = OptimalOperationsObserver(dispatcher, reference_schedule)

    # Valid available actions
    available_ops = dispatcher.available_operations()
    actions = [
        (op.operation_id, op.machine_id, op.job_id) for op in available_ops
    ]

    # Add an artificial non-optimal action tuple (invalid machine id)
    if actions:
        fake_action = (actions[0][0], actions[0][1] + 99, actions[0][2])
        actions_with_fake = actions + [fake_action]
    else:
        actions_with_fake = []

    mapping = get_optimal_actions(optimal_obs, actions_with_fake)

    # Fake action should be marked as non-optimal (0)
    if actions_with_fake:
        assert mapping[fake_action] == 0


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
