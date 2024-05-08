"""Home of the `CompositeFeatureObserver` class."""

from collections import defaultdict
import numpy as np

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_extraction import (
    FeatureObserver,
    FeatureType,
)


class CompositeFeatureObserver(FeatureObserver):
    """Aggregates features from other FeatureObserver instances subscribed to
    the same `Dispatcher` by concatenating their feature matrices along the
    first axis (horizontal concatenation)."""

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
        super().__init__(dispatcher)

    def initialize_features(self):
        features: dict[FeatureType, list[np.ndarray]] = defaultdict(list)
        for tracker in self.feature_observers:
            for feature_type, feature_matrix in tracker.features.items():
                features[feature_type].append(feature_matrix)

        self.features = {
            feature_type: np.concatenate(features, axis=1)
            for feature_type, features in features.items()
        }
