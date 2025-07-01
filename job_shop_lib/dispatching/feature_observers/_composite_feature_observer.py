"""Home of the `CompositeFeatureObserver` class."""

from collections import defaultdict
from collections.abc import Sequence

# The Self type can be imported directly from Python’s typing module in
# version 3.11 and beyond. We use the typing_extensions module to support
# python >=3.10
from typing_extensions import Self
import numpy as np
from numpy.typing import NDArray
import pandas as pd

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
    FeatureObserverConfig,
    feature_observer_factory,
    FeatureObserverType,
)


class CompositeFeatureObserver(FeatureObserver):
    """Aggregates features from other FeatureObserver instances subscribed to
    the same :class:`~job_shop_lib.dispatching.Dispatcher` by concatenating
    their feature matrices along the first axis (horizontal concatenation).

    It provides also a custom ``__str__`` method to display the features
    in a more readable way.

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
        feature_observers:
            A list of `FeatureObserver` instances to aggregate features from.
            If ``None``, all feature observers subscribed to the dispatcher are
            used.

    .. seealso::

        An example using this class can be found in the
        :doc:`../examples/08-Feature-Observers` example.

        Additionally, the class
        :class:`~job_shop_lib.reinforcement_learning.SingleJobShopGraphEnv`
        uses this feature observer to aggregate features from multiple
        ones.

    """

    __slots__ = {
        "feature_observers": (
            "List of :class:`FeatureObserver` instances to aggregate features "
            "from."
        ),
        "column_names": (
            "Dictionary mapping :class:`FeatureType` to a list of column "
            "names for the corresponding feature matrix. They are generated "
            "based on the class name of the :class:`FeatureObserver` instance "
            "that produced the feature."
        ),
    }

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        subscribe: bool = True,
        feature_types: list[FeatureType] | FeatureType | None = None,
        feature_observers: list[FeatureObserver] | None = None,
    ):
        if feature_observers is None:
            feature_observers = [
                observer
                for observer in dispatcher.subscribers
                if isinstance(observer, FeatureObserver)
            ]
        self.feature_observers = feature_observers
        self.column_names: dict[FeatureType, list[str]] = defaultdict(list)
        super().__init__(
            dispatcher, subscribe=subscribe, feature_types=feature_types
        )
        self._set_column_names()

    @classmethod
    def from_feature_observer_configs(
        cls,
        dispatcher: Dispatcher,
        feature_observer_configs: Sequence[
            str
            | FeatureObserverType
            | type[FeatureObserver]
            | FeatureObserverConfig
        ],
        subscribe: bool = True,
    ) -> Self:
        """Creates the composite feature observer.

        Args:
            dispatcher:
                The dispatcher used to create the feature observers.
            feature_observer_configs:
                The list of feature observer configuration objects.
            subscribe:
                Whether to subscribe the CompositeFeatureObserver to the
                dispatcher.
        """
        observers = [
            feature_observer_factory(observer_config, dispatcher=dispatcher)
            for observer_config in feature_observer_configs
        ]
        composite_observer = cls(
            dispatcher, feature_observers=observers, subscribe=subscribe
        )
        return composite_observer

    @property
    def features_as_dataframe(self) -> dict[FeatureType, pd.DataFrame]:
        """Returns the features as a dictionary of `pd.DataFrame` instances."""
        return {
            feature_type: pd.DataFrame(
                feature_matrix, columns=self.column_names[feature_type]
            )
            for feature_type, feature_matrix in self.features.items()
        }

    def initialize_features(self):
        features: dict[FeatureType, list[NDArray[np.float32]]] = defaultdict(
            list
        )
        for observer in self.feature_observers:
            for feature_type in self.supported_feature_types:
                feature_matrix = observer.features.get(feature_type)
                if feature_matrix is None:
                    continue
                features[feature_type].append(feature_matrix)

        self.features = {
            feature_type: np.concatenate(
                feature_matrices, axis=1  # type: ignore[misc]
            )
            for feature_type, feature_matrices in features.items()
        }

    def _set_column_names(self):
        for observer in self.feature_observers:
            for feature_type, feature_matrix in observer.features.items():
                feature_name = observer.__class__.__name__.replace(
                    "Observer", ""
                )
                if feature_matrix.shape[1] > 1:
                    self.column_names[feature_type] += [
                        f"{feature_name}_{i}"
                        for i in range(feature_matrix.shape[1])
                    ]
                else:
                    self.column_names[feature_type].append(feature_name)

    def __str__(self):
        out = [f"{self.__class__.__name__}:"]
        out.append("-" * (len(out[0]) - 1))
        for feature_type, dataframe in self.features_as_dataframe.items():
            out.append(f"{feature_type.value}:")
            out.append(dataframe.to_string())
        return "\n".join(out)
