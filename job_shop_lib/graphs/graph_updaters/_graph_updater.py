"""Home of the `GraphUpdater` class."""

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
        initial_job_shop_graph:
            The initial job shop graph. This is a copy of the graph that was
            received when the observer was created. It is used to reset the
            graph to its initial state.
        job_shop_graph:
            The current job shop graph. This is the graph that is updated
            after each scheduled operation.

    Args:
        dispatcher:
            The dispatcher instance to observe.
        job_shop_graph:
            The job shop graph to update.
        subscribe:
            Whether to subscribe to the dispatcher. If ``True``, the
            observer will subscribe to the dispatcher when it is
            initialized. If ``False``, the observer will not subscribe
            to the dispatcher.
    """

    def __init__(
        self,
        dispatcher: Dispatcher,
        job_shop_graph: JobShopGraph,
        *,
        subscribe: bool = True,
    ):
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
