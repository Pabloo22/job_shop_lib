"""Home of the `ResidualGraphUpdater` class."""

from job_shop_lib import ScheduledOperation
from job_shop_lib.graphs.graph_updaters import (
    GraphUpdater,
    remove_completed_operations,
)
from job_shop_lib.dispatching.feature_observers import (
    IsCompletedObserver,
    FeatureType,
)
from job_shop_lib.dispatching import create_or_get_observer, DispatcherObserver


class ResidualGraphUpdater(GraphUpdater):
    """Updates the residual graph based on the completed operations."""

    def __init__(
        self, dispatcher, job_shop_graph, is_singleton=False, subscribe=True
    ):
        """Initializes the residual graph updater.

        Args:
            dispatcher:
                The dispatcher instance to observe.
            job_shop_graph:
                The job shop graph to update.
            is_singleton:
                If True, ensures only one instance of this observer type is
                subscribed to the dispatcher. Defaults to False.
            subscribe:
                If True, automatically subscribes the observer to the
                dispatcher. Defaults to True.
        """
        super().__init__(
            dispatcher,
            job_shop_graph,
            is_singleton=is_singleton,
            subscribe=subscribe,
        )

        def has_machine_feature(observer: DispatcherObserver) -> bool:
            if not isinstance(observer, IsCompletedObserver):
                return False  # Make the type checker happy.
            return FeatureType.MACHINES in observer.features

        self.is_completed_observer = create_or_get_observer(
            dispatcher,
            IsCompletedObserver,
            condition=has_machine_feature,
            feature_types=[FeatureType.MACHINES],
            is_singleton=False,
        )

    def update(self, scheduled_operation: ScheduledOperation) -> None:
        """Updates the residual graph based on the completed operations."""
        remove_completed_operations(
            self.job_shop_graph,
            completed_operations=self.dispatcher.completed_operations(),
        )

        for machine_id, is_completed in enumerate(
            self.is_completed_observer.features[FeatureType.MACHINES].flatten()
        ):
            if is_completed != 1:
                continue
            machine_node = self.job_shop_graph.get_machine_node(machine_id)
            self.job_shop_graph.remove_node(machine_node.node_id)
