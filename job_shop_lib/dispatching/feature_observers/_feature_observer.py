"""Home of the `FeatureObserver` class and `FeatureType` enum."""

import enum
from typing import Optional, Union, Dict, List, Tuple

import numpy as np

from job_shop_lib import ScheduledOperation
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import Dispatcher, DispatcherObserver


class FeatureType(str, enum.Enum):
    """Types of features that can be extracted."""

    OPERATIONS = "operations"
    MACHINES = "machines"
    JOBS = "jobs"


class FeatureObserver(DispatcherObserver):
    """Base class for feature observers.

    A :class:`FeatureObserver` is a
    a subclass of :class:`~job_shop_lib.dispatching.DispatcherObserver` that
    observes features related to operations, machines, or jobs in the
    :class:`~job_shop_lib.dispatching.Dispatcher`.

    Attributes are stored in numpy arrays with a shape of (``num_entities``,
    ``feature_size``), where ``num_entities`` is the number of entities being
    observed (e.g., operations, machines, or jobs) and ``feature_size`` is the
    number of values being observed for each entity.

    The advantage of using arrays is that they can be easily updated in a
    vectorized manner, which is more efficient than updating each attribute
    individually. Furthermore, machine learning models can be trained on these
    arrays to predict the best dispatching decisions.

    Arrays use the data type ``np.float32``. This is because most machine

    New :class:`FeatureObservers` must inherit from this class, and re-define
    the class attributes ``_singleton`` (defualt ), ``_feature_size``
    (default 1) and ``_supported_feature_types`` (default all feature types).

    Feature observers are not singleton by default. This means that more than
    one instance of the same feature observer type can be subscribed to the
    dispatcher. This is useful when the first subscriber only observes a subset
    of the features, and the second subscriber observes a different subset of
    them. For example, the first subscriber could observe only the
    operation-related features, while the second subscriber could observe the
    jobs.

    Args:
        dispatcher:
            The :class:`~job_shop_lib.dispatching.Dispatcher` to observe.
        subscribe:
            If ``True``, the observer is subscribed to the dispatcher upon
            initialization. Otherwise, the observer must be subscribed later
            or manually updated.
        feature_types:
            A list of :class:`FeatureType` or a single :class:`FeatureType`
            that specifies the types of features to observe. They must be a
            subset of the class attribute :attr:`supported_feature_types`.
            If ``None``, all supported feature types are tracked.
    """

    _is_singleton = False
    _feature_sizes: Union[Dict[FeatureType, int], int] = 1
    _supported_feature_types = list(FeatureType)

    __slots__ = {
        "features": (
            "A dictionary of numpy arrays with the features. "
            "Each key is a :class:`FeatureType` and each value is a numpy "
            "array with the features. The array has shape (``num_entities``, "
            "``feature_size``), where ``num_entities`` is the number of "
            "entities being observed (e.g., operations, machines, or jobs) and"
            " ``feature_size`` is the number of values being observed for each"
            " entity."
        )
    }

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        subscribe: bool = True,
        feature_types: Optional[Union[List[FeatureType], FeatureType]] = None,
    ):
        feature_types = self._get_feature_types_list(feature_types)
        if isinstance(self._feature_sizes, int):
            feature_size = {
                feature_type: self._feature_sizes
                for feature_type in feature_types
            }
        super().__init__(dispatcher, subscribe=subscribe)

        number_of_entities = {
            FeatureType.OPERATIONS: dispatcher.instance.num_operations,
            FeatureType.MACHINES: dispatcher.instance.num_machines,
            FeatureType.JOBS: dispatcher.instance.num_jobs,
        }
        feature_dimensions = {
            feature_type: (
                number_of_entities[feature_type],
                feature_size[feature_type],
            )
            for feature_type in feature_types
        }
        self.features = {
            feature_type: np.zeros(
                feature_dimensions[feature_type],
                dtype=np.float32,
            )
            for feature_type in feature_types
        }
        self.initialize_features()

    @property
    def feature_sizes(self) -> Dict[FeatureType, int]:
        """Returns the size of the features.

        The size of the features is the number of values being observed for
        each entity. This corresponds to the second dimension of each array.

        This number is typically one (e.g. measuring the duration
        of each operation), but some feature observers like the
        :class:`CompositeFeatureObserver` may track more than one value.
        """
        if isinstance(self._feature_sizes, int):
            return {
                feature_type: self._feature_sizes
                for feature_type in self.features
            }
        return self._feature_sizes

    @property
    def supported_feature_types(self) -> List[FeatureType]:
        """Returns the supported feature types."""
        return self._supported_feature_types

    @property
    def feature_dimensions(self) -> Dict[FeatureType, Tuple[int, int]]:
        """A dictionary containing the shape of each :class:`FeatureType`."""
        feature_dimensions = {}
        for feature_type, array in self.features.items():
            feature_dimensions[feature_type] = array.shape
        return feature_dimensions  # type: ignore[return-value]

    def initialize_features(self):
        """Initializes the features based on the current state of the
        dispatcher.

        This method is automatically called after initializing the observer.
        """

    def update(self, scheduled_operation: ScheduledOperation):
        """Updates the features based on the scheduled operation.

        By default, this method just calls :meth:`initialize_features`.

        Args:
            ScheduledOperation:
                The operation that has been scheduled.
        """
        self.initialize_features()

    def reset(self):
        """Sets features to zero and calls to :meth:``initialize_features``."""
        self.set_features_to_zero()
        self.initialize_features()

    def set_features_to_zero(
        self, exclude: Optional[Union[FeatureType, List[FeatureType]]] = None
    ):
        """Sets all features to zero except for the ones specified in
        ``exclude``.

        Setting a feature to zero means that all values in the feature array
        are set to this value.

        Args:
            exclude:
                A single :class:`FeatureType` or a list of :class:`FeatureType`
                that specifies the features that should not be set to zero. If
                ``None``, all currently used features are set to zero.
        """
        if exclude is None:
            exclude = []
        if isinstance(exclude, FeatureType):
            exclude = [exclude]

        for feature_type in self.features:
            if feature_type in exclude:
                continue
            self.features[feature_type][:] = 0.0

    def _get_feature_types_list(
        self,
        feature_types: Optional[Union[List[FeatureType], FeatureType]],
    ) -> List[FeatureType]:
        """Returns a list of feature types.

        Args:
            feature_types:
                A list of feature types or a single feature type. If ``None``,
                all feature types are returned.
        """
        if isinstance(feature_types, FeatureType):
            return [feature_types]
        if feature_types is None:
            return self._supported_feature_types

        for feature_type in feature_types:
            if feature_type not in self._supported_feature_types:
                raise ValidationError(
                    f"Feature type {feature_type} is not supported."
                    " Supported feature types are: "
                    f"{self._supported_feature_types}"
                )
        return feature_types

    def __str__(self):
        out = [self.__class__.__name__, ":\n"]
        out.append("-" * len(out[0]))
        for feature_type, feature in self.features.items():
            out.append(f"\n{feature_type.value}:\n{feature}")
        return "".join(out)
