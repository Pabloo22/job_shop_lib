import pytest
import numpy as np
from numpy.typing import NDArray

from job_shop_lib.exceptions import ValidationError
from job_shop_lib.reinforcement_learning import (
    add_padding,
    create_edge_type_dict,
    map_values,
)


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


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
