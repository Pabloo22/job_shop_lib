from job_shop_lib import BaseSolver, JobShopInstance, Schedule
from job_shop_lib.metaheuristics import JobShopAnnealer
from job_shop_lib.dispatching.rules import DispatchingRuleSolver
from job_shop_lib.metaheuristics import (
    NeighborGenerator,
    swap_in_critical_path,
    ObjectiveFunction,
)


class SimulatedAnnealingSolver(BaseSolver):
    """Wraps the :class:`JobShopAnnealer` to follow the
    :class`~job_shop_lib.BaseSolver` interface.

    .. seealso::
        See the documentation of the :class:`JobShopAnnealer` class for more
        details on the annealing process.

    Attributes:
        initial_temperature:
            Initial temperature for the annealing process. It controls the
            probability of accepting worse solutions. That sets the metropolis
            criterion. Corresponds to the `tmax` parameter in the annealer.
        ending_temperature:
            Ending temperature for the annealing process. It controls when to
            stop accepting worse solutions. Corresponds to the `tmin` parameter
            in the annealer.
        steps:
            Number of steps to perform in the annealing process. This is the
            number of iterations the algorithm will run.
        updates:
            The number of progress updates to print during the annealing
            process. Set to 0 to disable updates.
        seed:
            Random seed for reproducibility. If ``None``, random behavior will
            be non-deterministic.

    Args:
        initial_temperature:
            Initial temperature for the annealing process. It controls the
            probability of accepting worse solutions. That sets the metropolis
            criterion. Corresponds to the `tmax` parameter in the annealer.
        ending_temperature:
            Ending temperature for the annealing process. It controls when to
            stop accepting worse solutions. Corresponds to the `tmin` parameter
            in the annealer.
        steps:
            Number of steps to perform in the annealing process. This is the
            number of iterations the algorithm will run.
        updates:
            The number of progress updates to print during the annealing
            process. Set to 0 to disable updates.
        seed:
            Random seed for reproducibility. If ``None``, random behavior will
            be non-deterministic.
    """

    def __init__(
        self,
        *,
        initial_temperature: float = 25000,
        ending_temperature: float = 2.5,
        steps: int = 50_000,
        updates: int = 100,
        objective_function: ObjectiveFunction | None = None,
        seed: int | None = None,
        neighbor_generator: NeighborGenerator = swap_in_critical_path,
    ):
        self.initial_temperature = initial_temperature
        self.ending_temperature = ending_temperature
        self.steps = steps
        self.updates = updates
        self.objective_function = objective_function
        self.seed = seed
        self.neighbor_generator = neighbor_generator
        self.annealer_: JobShopAnnealer | None = None

    def setup_annealer(
        self, instance: JobShopInstance, initial_state: Schedule | None = None
    ) -> None:
        """Initializes the annealer with the given instance and initial state.

        Args:
            instance:
                The job shop instance to solve.
            initial_state:
                Initial state of the schedule as a list of lists, where each
                sublist represents the operations of a job.
        """
        if initial_state is None:
            initial_state = self._generate_initial_state(instance)

        annealer = JobShopAnnealer(
            instance,
            initial_state,
            objective_function=self.objective_function,
            seed=self.seed,
            neighbor_generator=self.neighbor_generator,
        )
        best_hparams = {
            "tmax": self.initial_temperature,
            "tmin": self.ending_temperature,
            "steps": self.steps,
            "updates": self.updates,
        }
        annealer.set_schedule(best_hparams)
        self.annealer_ = annealer

    def solve(
        self,
        instance: JobShopInstance,
        initial_state: Schedule | None = None,
    ) -> Schedule:
        """Solves the given Job Shop Scheduling problem using
        simulated annealing.

        Args:
            instance:
                The job shop problem instance to solve.
            initial_state:
                Initial job sequences for each machine. A job sequence is a
                list of job ids. Each list of job ids represents the order of
                operations on the machine. The machine that the list
                corresponds to is determined by the index of the list. If
                ``None``, the solver will generate an initial state using the
                :class:`DispatchingRuleSolver`.

        Returns:
            The best schedule found.

        """
        self.setup_annealer(instance, initial_state)
        # For type checking purposes, we assert that the annealer is set up.
        assert (
            self.annealer_ is not None
        ), "There was a problem setting up the annealer."
        try:
            best_state, _ = self.annealer_.anneal()
        except KeyboardInterrupt:
            # If the annealing process is interrupted, we return the best state
            # found so far.
            best_state = self.annealer_.best_state
        return best_state

    @staticmethod
    def _generate_initial_state(instance: JobShopInstance) -> Schedule:
        """Uses the
        :class:`~job_shop_lib.dispatching.rules.DispatchingRuleSolver` to
        generate an initial state for the annealer.

        .. note::
            The first solution might be unfeasible if the job shop instance
            has deadlines.

        Args:
            instance (JobShopInstance): The job shop problem instance.

        Returns:
            An initial schedule generated by the dispatching rule solver.
        """
        solver = DispatchingRuleSolver()
        schedule = solver.solve(instance)
        return schedule
