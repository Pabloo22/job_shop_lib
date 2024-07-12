"""Home of the `GraphBuilderObserver` class."""

from abc import abstractmethod
from copy import deepcopy

from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching import DispatcherObserver, Dispatcher
from job_shop_lib.graphs import JobShopGraph


class GraphUpdater(DispatcherObserver):
    """Observer that builds and updates a job shop graph.

    This observer uses a provided graph builder function to initialize the
    job shop graph and a graph updater function to update the graph after
    each scheduled operation.

    Attributes:
        dispatcher:
            The dispatcher instance to observe.
        graph_initializer:
            A function that builds the initial job shop graph from a job shop
            instance.
        graph_updater:
            A function that updates the job shop graph based on the
            dispatcher state and a scheduled operation.
        job_shop_graph:
            The job shop graph being managed and updated.
    """

    def __init__(
        self,
        dispatcher: Dispatcher,
        job_shop_graph: JobShopGraph,
        *,
        subscribe: bool = True,
    ):
        """
        Args:
            dispatcher:
                The dispatcher instance to observe.
            graph_initializer:
                A function that builds the initial job shop graph from a job
                shop instance.
            graph_updater:
                A function that updates the job shop graph based on the
                dispatcher state and a scheduled operation.
            subscribe:
                If True, automatically subscribes the observer to the
                dispatcher. Defaults to True.
        """
        super().__init__(dispatcher, subscribe=subscribe)
        self.initial_job_shop_graph = deepcopy(job_shop_graph)
        self.job_shop_graph = job_shop_graph

    def reset(self) -> None:
        """Resets the job shop graph."""
        self.job_shop_graph = deepcopy(self.initial_job_shop_graph)

    @abstractmethod
    def update(self, scheduled_operation: ScheduledOperation) -> None:
        """Updates the job shop graph after an operation has been
        dispatched."""
