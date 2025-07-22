"""Tests for the FeatureObserver class."""

import pytest
import numpy as np

from job_shop_lib import JobShopInstance, ScheduledOperation
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)
from job_shop_lib.exceptions import ValidationError


class ConcreteFeatureObserver(FeatureObserver):
    """Concrete implementation of FeatureObserver for testing."""

    def initialize_features(self):
        """Initialize with some test values."""
        for _, array in self.features.items():
            array.fill(1.0)


class CustomFeatureSizeObserver(FeatureObserver):
    """Feature observer with custom feature sizes."""

    _feature_sizes = {
        FeatureType.OPERATIONS: 3,
        FeatureType.MACHINES: 2,
        FeatureType.JOBS: 1,
    }

    def initialize_features(self):
        """Initialize with test values."""
        for _, array in self.features.items():
            array.fill(2.0)


class LimitedSupportObserver(FeatureObserver):
    """Observer that only supports OPERATIONS and MACHINES."""

    _supported_feature_types = [FeatureType.OPERATIONS, FeatureType.MACHINES]

    def initialize_features(self):
        pass


class TestFeatureType:
    """Tests for the FeatureType enum."""

    def test_feature_type_values(self):
        """Test that FeatureType has the expected values."""
        assert FeatureType.OPERATIONS == "operations"
        assert FeatureType.MACHINES == "machines"
        assert FeatureType.JOBS == "jobs"

    def test_feature_type_enum_inheritance(self):
        """Test that FeatureType inherits from str and enum.Enum."""
        assert isinstance(FeatureType.OPERATIONS, str)
        assert issubclass(FeatureType, str)


class TestFeatureObserver:
    """Tests for the FeatureObserver class."""

    def test_init_default_parameters(self, dispatcher):
        """Test initialization with default parameters."""
        observer = ConcreteFeatureObserver(dispatcher)

        # Check that all feature types are tracked by default
        assert set(observer.features.keys()) == {
            FeatureType.OPERATIONS,
            FeatureType.MACHINES,
            FeatureType.JOBS,
        }

        # Check array shapes
        assert observer.features[FeatureType.OPERATIONS].shape == (
            dispatcher.instance.num_operations,
            1,
        )
        assert observer.features[FeatureType.MACHINES].shape == (
            dispatcher.instance.num_machines,
            1,
        )
        assert observer.features[FeatureType.JOBS].shape == (
            dispatcher.instance.num_jobs,
            1,
        )

        # Check data type
        for array in observer.features.values():
            assert array.dtype == np.float32

        # Check that initialize_features was called
        for array in observer.features.values():
            assert np.all(array == 1.0)

    def test_init_single_feature_type(self, dispatcher):
        """Test initialization with a single feature type."""
        observer = ConcreteFeatureObserver(
            dispatcher, feature_types=FeatureType.OPERATIONS
        )

        assert list(observer.features.keys()) == [FeatureType.OPERATIONS]
        assert observer.features[FeatureType.OPERATIONS].shape == (
            dispatcher.instance.num_operations,
            1,
        )

    def test_init_list_feature_types(self, dispatcher):
        """Test initialization with a list of feature types."""
        feature_types = [FeatureType.OPERATIONS, FeatureType.MACHINES]
        observer = ConcreteFeatureObserver(
            dispatcher, feature_types=feature_types
        )

        assert set(observer.features.keys()) == set(feature_types)

    def test_init_without_subscription(self, dispatcher):
        """Test initialization without auto-subscription."""
        observer = ConcreteFeatureObserver(dispatcher, subscribe=False)

        # Observer should not be in dispatcher's subscribers
        assert observer not in dispatcher.subscribers

    def test_init_with_custom_feature_sizes_dict(self, dispatcher):
        """Test initialization with custom feature sizes as dictionary."""
        observer = CustomFeatureSizeObserver(dispatcher)

        expected_shapes = {
            FeatureType.OPERATIONS: (dispatcher.instance.num_operations, 3),
            FeatureType.MACHINES: (dispatcher.instance.num_machines, 2),
            FeatureType.JOBS: (dispatcher.instance.num_jobs, 1),
        }

        for feature_type, expected_shape in expected_shapes.items():
            assert observer.features[feature_type].shape == expected_shape

    def test_init_with_unsupported_feature_type(self, dispatcher):
        """Test initialization with unsupported feature type raises error."""
        # Use an observer that doesn't support JOBS
        with pytest.raises(
            ValidationError,
        ):
            LimitedSupportObserver(
                dispatcher, feature_types=[FeatureType.JOBS]
            )

    def test_feature_sizes_property_int(self, dispatcher):
        """Test feature_sizes property when _feature_sizes is int."""
        observer = ConcreteFeatureObserver(dispatcher)

        expected = {
            FeatureType.OPERATIONS: 1,
            FeatureType.MACHINES: 1,
            FeatureType.JOBS: 1,
        }
        assert observer.feature_sizes == expected

    def test_feature_sizes_property_dict(self, dispatcher):
        """Test feature_sizes property when _feature_sizes is dict."""
        observer = CustomFeatureSizeObserver(dispatcher)

        expected = {
            FeatureType.OPERATIONS: 3,
            FeatureType.MACHINES: 2,
            FeatureType.JOBS: 1,
        }
        assert observer.feature_sizes == expected

    def test_supported_feature_types_property(self, dispatcher):
        """Test supported_feature_types property."""
        observer = ConcreteFeatureObserver(dispatcher)
        assert observer.supported_feature_types == list(FeatureType)

        limited_observer = LimitedSupportObserver(dispatcher)
        assert limited_observer.supported_feature_types == [
            FeatureType.OPERATIONS,
            FeatureType.MACHINES,
        ]

    def test_feature_dimensions_property(self, dispatcher):
        """Test feature_dimensions property."""
        observer = ConcreteFeatureObserver(dispatcher)

        expected = {
            FeatureType.OPERATIONS: (dispatcher.instance.num_operations, 1),
            FeatureType.MACHINES: (dispatcher.instance.num_machines, 1),
            FeatureType.JOBS: (dispatcher.instance.num_jobs, 1),
        }

        assert observer.feature_dimensions == expected

    def test_update_method(self, dispatcher):
        """Test the update method."""
        observer = ConcreteFeatureObserver(dispatcher)

        # Set features to different values
        for array in observer.features.values():
            array.fill(5.0)

        # Create a dummy scheduled operation
        operation = dispatcher.instance.jobs[0][0]
        scheduled_op = ScheduledOperation(operation, 0, 0)

        # Call update - should reinitialize features to 1.0
        observer.update(scheduled_op)

        for array in observer.features.values():
            assert np.all(array == 1.0)

    def test_reset_method(self, dispatcher):
        """Test the reset method."""
        observer = ConcreteFeatureObserver(dispatcher)

        # Modify features
        for array in observer.features.values():
            array.fill(5.0)

        # Reset should set to zero then reinitialize to 1.0
        observer.reset()

        for array in observer.features.values():
            assert np.all(array == 1.0)

    def test_set_features_to_zero_all(self, dispatcher):
        """Test set_features_to_zero with no exclusions."""
        observer = ConcreteFeatureObserver(dispatcher)

        # Set features to non-zero values
        for array in observer.features.values():
            array.fill(5.0)

        observer.set_features_to_zero()

        for array in observer.features.values():
            assert np.all(array == 0.0)

    def test_set_features_to_zero_single_exclude(self, dispatcher):
        """Test set_features_to_zero with single exclusion."""
        observer = ConcreteFeatureObserver(dispatcher)

        # Set features to non-zero values
        for array in observer.features.values():
            array.fill(5.0)

        observer.set_features_to_zero(exclude=FeatureType.OPERATIONS)

        # Operations should remain unchanged
        assert np.all(observer.features[FeatureType.OPERATIONS] == 5.0)
        # Others should be zero
        assert np.all(observer.features[FeatureType.MACHINES] == 0.0)
        assert np.all(observer.features[FeatureType.JOBS] == 0.0)

    def test_set_features_to_zero_list_exclude(self, dispatcher):
        """Test set_features_to_zero with list of exclusions."""
        observer = ConcreteFeatureObserver(dispatcher)

        # Set features to non-zero values
        for array in observer.features.values():
            array.fill(5.0)

        exclude_list = [FeatureType.OPERATIONS, FeatureType.MACHINES]
        observer.set_features_to_zero(exclude=exclude_list)

        # Excluded should remain unchanged
        assert np.all(observer.features[FeatureType.OPERATIONS] == 5.0)
        assert np.all(observer.features[FeatureType.MACHINES] == 5.0)
        # Jobs should be zero
        assert np.all(observer.features[FeatureType.JOBS] == 0.0)

    def test_get_feature_types_list_none(self, dispatcher):
        """Test _get_feature_types_list with None input."""
        observer = ConcreteFeatureObserver(dispatcher, subscribe=False)
        # pylint: disable=protected-access
        result = observer._get_feature_types_list(None)
        assert result == list(FeatureType)

    def test_get_feature_types_list_single(self, dispatcher):
        """Test _get_feature_types_list with single FeatureType input."""
        observer = ConcreteFeatureObserver(dispatcher, subscribe=False)
        # pylint: disable=protected-access
        result = observer._get_feature_types_list(FeatureType.OPERATIONS)
        assert result == [FeatureType.OPERATIONS]

    def test_get_feature_types_list_valid_list(self, dispatcher):
        """Test _get_feature_types_list with valid list input."""
        observer = ConcreteFeatureObserver(dispatcher, subscribe=False)
        input_list = [FeatureType.OPERATIONS, FeatureType.MACHINES]
        # pylint: disable=protected-access
        result = observer._get_feature_types_list(input_list)
        assert result == input_list

    def test_get_feature_types_list_invalid(self, dispatcher):
        """Test _get_feature_types_list with invalid feature type."""
        observer = LimitedSupportObserver(dispatcher, subscribe=False)

        with pytest.raises(
            ValidationError,
        ):
            # pylint: disable=protected-access
            observer._get_feature_types_list([FeatureType.JOBS])

    def test_str_method(self, dispatcher):
        """Test the __str__ method."""
        observer = ConcreteFeatureObserver(
            dispatcher, feature_types=FeatureType.OPERATIONS
        )

        str_repr = str(observer)

        # Should contain class name
        assert "ConcreteFeatureObserver" in str_repr
        # Should contain feature type
        assert "operations" in str_repr
        # Should contain array representation
        assert "[[1.]" in str_repr or "[1.]" in str_repr

    def test_str_method_multiple_features(self, dispatcher):
        """Test __str__ method with multiple feature types."""
        observer = ConcreteFeatureObserver(dispatcher)

        str_repr = str(observer)

        # Should contain all feature types
        assert "operations" in str_repr
        assert "machines" in str_repr
        assert "jobs" in str_repr

    def test_class_attributes(self):
        """Test class attributes have correct default values."""
        # pylint: disable=protected-access
        assert FeatureObserver._is_singleton is False  
        assert FeatureObserver._feature_sizes == 1
        assert FeatureObserver._supported_feature_types == list(FeatureType)

    def test_inheritance(self, dispatcher):
        """Test that FeatureObserver properly inherits from DispatcherObserver."""
        from job_shop_lib.dispatching import DispatcherObserver

        observer = ConcreteFeatureObserver(dispatcher)
        assert isinstance(observer, DispatcherObserver)

    def test_slots_attribute(self):
        """Test that __slots__ is properly defined."""
        assert hasattr(FeatureObserver, "__slots__")
        assert "features" in FeatureObserver.__slots__

    def test_edge_case_empty_instance(self):
        """Test with an edge case instance that has no operations."""
        # Create minimal instance with empty jobs
        jobs: list = []
        instance = JobShopInstance(jobs, "Empty")
        dispatcher = Dispatcher(instance)

        observer = ConcreteFeatureObserver(dispatcher)

        # Should handle zero-sized arrays gracefully
        assert observer.features[FeatureType.OPERATIONS].shape == (0, 1)
        assert observer.features[FeatureType.MACHINES].shape == (0, 1)
        assert observer.features[FeatureType.JOBS].shape == (0, 1)

    def test_feature_array_modification(self, dispatcher):
        """Test that feature arrays can be modified directly."""
        observer = ConcreteFeatureObserver(dispatcher)

        # Modify arrays directly
        observer.features[FeatureType.OPERATIONS][0, 0] = 99.0

        assert observer.features[FeatureType.OPERATIONS][0, 0] == 99.0

    def test_numpy_float32_dtype(self, dispatcher):
        """Test that arrays use np.float32 dtype."""
        observer = ConcreteFeatureObserver(dispatcher)

        for array in observer.features.values():
            assert array.dtype == np.float32

    def test_feature_observer_not_singleton_by_default(self, dispatcher):
        """Test that feature observers are not singleton by default."""
        observer1 = ConcreteFeatureObserver(dispatcher)
        observer2 = ConcreteFeatureObserver(dispatcher)

        # Both should be in subscribers list
        assert observer1 in dispatcher.subscribers
        assert observer2 in dispatcher.subscribers
