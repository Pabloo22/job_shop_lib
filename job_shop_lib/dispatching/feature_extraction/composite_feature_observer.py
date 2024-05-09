"""Home of the `CompositeFeatureObserver` class."""

from collections import defaultdict
import numpy as np
import pandas as pd

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_extraction import (
    FeatureObserver,
    FeatureType,
)


class CompositeFeatureObserver(FeatureObserver):
    """Aggregates features from other FeatureObserver instances subscribed to
    the same `Dispatcher` by concatenating their feature matrices along the
    first axis (horizontal concatenation).

    Attributes:
        feature_observers:
            List of `FeatureObserver` instances to aggregate features from.
        column_names:
            Dictionary mapping `FeatureType` to a list of column names for the
            corresponding feature matrix.
    """

    def __init__(
        self,
        dispatcher: Dispatcher,
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
        super().__init__(dispatcher)
        self._set_column_names()

    def initialize_features(self):
        features: dict[FeatureType, list[np.ndarray]] = defaultdict(list)
        for observer in self.feature_observers:
            for feature_type, feature_matrix in observer.features.items():
                features[feature_type].append(feature_matrix)

        self.features = {
            feature_type: np.concatenate(features, axis=1)
            for feature_type, features in features.items()
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
        out = [f"{self.__class__.__name__}:\n"]
        out.append("-" * (len(out[0]) - 1))
        for feature_type, feature_matrix in self.features.items():
            df = pd.DataFrame(
                feature_matrix, columns=self.column_names[feature_type]
            )
            out.append(
                (f"\n{feature_type.value} features:\n" f"{df.to_string()}\n")
            )
        return "\n".join(out)
