"""Home of the `CompositeFeatureObserver` class."""

import numpy as np

from job_shop_lib import JobShopLibError
from job_shop_lib.graphs import NodeType
from job_shop_lib.dispatching.feature_extraction import FeatureObserver


class CompositeFeatureObserver(FeatureObserver):
    """Feature creator that combines multiple feature creators."""

    def initialize_features(self):
        trackers = self._get_trackers()
        node_features: dict[NodeType, list[np.ndarray]] = {
            node_type: [] for node_type in self.graph.nodes_by_type
        }
        for tracker in trackers:
            for node_type, features in tracker.node_features.items():
                if features.size > 0:
                    node_features[node_type].append(features)

        self.node_features = {
            node_type: np.concatenate(features, axis=1)
            for node_type, features in node_features.items()
        }

    def _get_trackers(self) -> list[FeatureObserver]:
        trackers = [
            subscriber
            for subscriber in self.dispatcher.subscribers
            if isinstance(subscriber, FeatureObserver)
        ]
        if trackers[-1] is not self:
            raise JobShopLibError(
                "The last subscriber must be the CompositeFeatureObserver."
            )
        trackers.pop()
        return trackers
