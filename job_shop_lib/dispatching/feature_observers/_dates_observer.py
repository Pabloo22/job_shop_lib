"""Home of the `DatesObserver` class."""

from typing import Literal

import numpy as np

from job_shop_lib import ScheduledOperation, JobShopInstance
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
)

Attribute = Literal["release_date", "deadline", "due_date"]


class DatesObserver(FeatureObserver):
    """Observes time-related attributes of operations.

    This observer tracks attributes like release date, deadline, and
    due date for each operation in the job shop instance. The attributes to
    be observed can be specified during initialization.

    The values are stored in a numpy array of shape ``(num_operations,
    num_attributes)``, where ``num_attributes`` is the number of attributes
    being observed.

    All attributes are updated based on the current time of the dispatcher so
    that they reflect the relative time remaining until the event occurs:
    (attribute - current_time). This means that the values will be negative if
    the event is in the past.

    Args:
        dispatcher:
            The :class:`~job_shop_lib.dispatching.Dispatcher` to observe.
        subscribe:
            If ``True``, the observer is subscribed to the dispatcher upon
            initialization. Otherwise, the observer must be subscribed later
            or manually updated.
        attributes_to_observe:
            A list of attributes to observe. If ``None``, all available time
            attributes (release_date, deadline, due_date) will be
            observed, provided they exist in the instance.
    """

    _supported_feature_types = [FeatureType.OPERATIONS]

    __slots__ = {
        "attributes_to_observe": "List of attributes to observe.",
        "_attribute_map": "Maps attributes to their column index.",
    }

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        subscribe: bool = True,
        attributes_to_observe: list[Attribute] | None = None,
        feature_types: FeatureType | list[FeatureType] | None = None,
    ):
        self.attributes_to_observe = self._determine_attributes_to_observe(
            dispatcher.instance, attributes_to_observe
        )
        self._attribute_map = {
            attr: i for i, attr in enumerate(self.attributes_to_observe)
        }
        self._previous_current_time = 0
        super().__init__(
            dispatcher,
            subscribe=subscribe,
            feature_types=feature_types,
        )

    @property
    def feature_sizes(self) -> dict[FeatureType, int]:
        return {
            FeatureType.OPERATIONS: len(self.attributes_to_observe),
        }

    @property
    def attribute_map(self) -> dict[Attribute, int]:
        """Maps attributes to their column index in the features array."""
        return self._attribute_map

    def initialize_features(self):
        """Initializes the features for the operations.

        This method sets up the features for the operations based on the
        attributes to observe. It creates a numpy array with the shape
        (num_operations, num_attributes) and fills it with the corresponding
        values from the job shop instance. Note that the matrix may contain
        ``np.nan`` values for operations that do not have deadlines or
        due dates.

        .. seealso::
            - :meth:`job_shop_lib.JobShopInstance.release_dates_matrix_array`
            - :meth:`job_shop_lib.JobShopInstance.deadlines_matrix_array`
            - :meth:`job_shop_lib.JobShopInstance.due_dates_matrix_array`
        """
        self.features = {
            FeatureType.OPERATIONS: np.zeros(
                (
                    self.dispatcher.instance.num_operations,
                    len(self.attributes_to_observe),
                ),
                dtype=np.float32,
            )
        }
        self._previous_current_time = self.dispatcher.current_time()
        release_dates_matrix = (
            self.dispatcher.instance.release_dates_matrix_array
        )
        valid_operations_mask = ~np.isnan(release_dates_matrix.flatten())

        for attr, col_idx in self._attribute_map.items():
            matrix = getattr(self.dispatcher.instance, f"{attr}s_matrix_array")
            values = np.array(matrix).flatten()
            valid_values = values[valid_operations_mask]
            self.features[FeatureType.OPERATIONS][:, col_idx] = valid_values

    def update(self, scheduled_operation: ScheduledOperation):
        """Updates the features based on the scheduled operation.

        This method updates the features by subtracting the current time from
        the initial release date, deadline, and due date attributes of the
        operations.

        Args:
            scheduled_operation:
                The scheduled operation that has just been processed. It is
                not used in this observer, but is required by the
                :meth:`FeatureObserver.update` method.
        """
        current_time = self.dispatcher.current_time()
        elapsed_time = current_time - self._previous_current_time
        self._previous_current_time = current_time
        cols = [
            self._attribute_map[attr]
            for attr in self.attributes_to_observe
        ]
        self.features[FeatureType.OPERATIONS][:, cols] -= elapsed_time

    def _determine_attributes_to_observe(
        self,
        instance: JobShopInstance,
        attributes_to_observe: list[Attribute] | None,
    ) -> list[Attribute]:
        if attributes_to_observe:
            return attributes_to_observe

        default_attributes: list[Attribute] = []
        if instance.has_release_dates:
            default_attributes.append("release_date")
        if instance.has_deadlines:
            default_attributes.append("deadline")
        if instance.has_due_dates:
            default_attributes.append("due_date")
        return default_attributes

    def reset(self):
        """Calls :meth:`initialize_features`"""
        self.initialize_features()
