"""A Feature Extractor computes features from a graph and a dispatcher."""

from abc import abstractmethod

import numpy as np
from job_shop_lib import JobShopLibError, ScheduledOperation
from job_shop_lib.graphs import JobShopGraph, NodeType
from job_shop_lib.dispatching import Dispatcher, DispatcherObserver


class FeatureObserver(DispatcherObserver):
    """Base class for node feature extractors."""

    def __init__(self, dispatcher: Dispatcher, graph: JobShopGraph):
        if dispatcher.instance is not graph.instance:
            raise JobShopLibError(
                "The dispatcher and the graph must have the same instance."
            )
        super().__init__(dispatcher)
        self.graph = graph
        self.node_features: dict[NodeType, np.ndarray] = {}
        self.initialize_features()

    @abstractmethod
    def initialize_features(self):
        """Creates the features for the nodes in the graph."""

    def update(self, scheduled_operation: ScheduledOperation):
        """Updates the features of the nodes in the graph."""
        self.initialize_features()

    def reset(self):
        """Resets the node features to their initial values."""
        self.initialize_features()
