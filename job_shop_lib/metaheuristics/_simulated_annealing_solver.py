from job_shop_lib import BaseSolver, JobShopInstance, Schedule
from job_shop_lib.metaheuristics import JobShopAnnealer
from job_shop_lib.dispatching.rules import DispatchingRuleSolver


class SimulatedAnnealingSolver(BaseSolver):
    """Wraps the :class:`JobShopAnnealer` to follow the
    :class``~job_shop_lib.BaseSolver`` interface.

    .. seealso::
        See the documentation of the :class:`JobShopAnnealer` class for more
        details on the annealing process.

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
        deadline_penalty_factor:
            Factor to penalize deadline violations. If a deadline is not met,
            it will add this quantity to the makespan to get the energy
            of the solution.
        due_date_penalty_factor:
            Factor to penalize due date violations. If a due date is not met,
            it will add this quantity to the makespan to get the energy
            of the solution.
        seed:
            Random seed for reproducibility. If ``None``, random behavior will
            be non-deterministic.
        time_budget_in_minutes:
            Optional time budget in minutes for the annealing process. If set,
            the solver will automatically determine the best parameters based
            on this budget.

            .. seealso::
                The :meth:`JobShopAnnealer.auto` method for details on how the
                parameters are determined based on the time budget.

            .. warning::
                If this parameter is set, the ``initial_temperature``,
                ``ending_temperature``, and ``steps`` parameters will be
                ignored.
        auto_steps:
            Number of steps to use when determining the best parameters
            automatically based on the time budget. This is used by the
            :meth:`JobShopAnnealer.auto` method to find reasonable parameters
            for the annealing process. It does not have any effect if
            ``time_budget_in_minutes`` is not set. Default is 2000.
    """

    def __init__(
        self,
        initial_temperature: float = 25000,
        ending_temperature: float = 2.5,
        steps: int = 50_000,
        updates: int = 100,
        deadline_penalty_factor: int = 1_000_000,
        due_date_penalty_factor: int = 100,
        seed: int | None = None,
        time_budget_in_minutes: float | None = None,
        auto_steps: int = 2000,
    ):
        self.initial_temperature = initial_temperature
        self.ending_temperature = ending_temperature
        self.steps = steps
        self.updates = updates
        self.deadline_penalty_factor = deadline_penalty_factor
        self.due_date_penalty_factor = due_date_penalty_factor
        self.seed = seed
        self.time_budget_in_minutes = time_budget_in_minutes
        self.auto_steps = auto_steps

    def solve(
        self,
        instance: JobShopInstance,
        initial_state: list[list[int]] | None = None,
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
        if initial_state is None:
            initial_state = self._generate_initial_state(instance)

        annealer = JobShopAnnealer(
            instance,
            initial_state,
            deadline_penalty_factor=self.deadline_penalty_factor,
            due_date_penalty_factor=self.due_date_penalty_factor,
            seed=self.seed,
        )
        if self.time_budget_in_minutes is not None:
            best_hparams = annealer.auto(
                minutes=self.time_budget_in_minutes, steps=self.auto_steps
            )
        else:
            best_hparams = {
                "tmax": self.initial_temperature,
                "tmin": self.ending_temperature,
                "steps": self.steps,
                "updates": self.updates,
            }
        annealer.set_schedule(best_hparams)

        try:
            best_state, _ = annealer.anneal()
        except InterruptedError:
            # If the annealing process is interrupted, we return the best state
            # found so far.
            best_state = annealer.best_state
        return Schedule.from_job_sequences(instance, best_state)

    @staticmethod
    def _generate_initial_state(instance: JobShopInstance) -> list[list[int]]:
        """Uses the
        :class:`~job_shop_lib.dispatching.rules.DispatchingRuleSolver` to
        generate an initial state for the annealer.

        .. note::
            The first solution might be unfeasible if the job shop instance
            has deadlines.

        Args:
            instance (JobShopInstance): The job shop problem instance.

        Returns:
            list[list[int]]: Initial state as a list of lists, where each
            sublist represents the operations of a job.
        """
        solver = DispatchingRuleSolver()
        schedule = solver.solve(instance)
        return schedule.job_sequences()
