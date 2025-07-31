import random
from job_shop_lib import BaseSolver, JobShopInstance, Schedule
from job_shop_lib.metaheuristics import JobShopAnnealer


class SimulatedAnnealingSolver(BaseSolver):
    """Simulated Annealing Solver for Job Shop Scheduling.

    SA (Simulated Annealing) is a probabilistic technique (metaheuristic
    algorithm) for approximating the global optimum of a given function.
    It seeks to find a good approximation of the optimized makespan by
    exploring the schedule space and accepting worse schedules with evaluating
    the metropolis criterion. It represents the JSSP solution by defining
    the objective function that complies with the constraints of the arrival
    times and deadlines.

    Attributes:
        initial_temperature: Initial temperature for the annealing process.
        steps: Number of steps to perform in the annealing process.
        cool: Cooling factor for the temperature.
        penalty_factor: Factor to scale the penalty for infeasible solutions.
        seed: Random seed for reproducible results.

    Args:
        initial_temperature:
            Initial temperature for the annealing process. It controls the
            probability of accepting worse solutions. That sets the metropolis
            criterion.
        steps:
            Number of steps to perform in the annealing process. It is
            crucial for the convergence of the algorithm. It also specfies
            how many iterations will be performed. Therefore, user can control
            the expensiveness of the algorithm.
        cool:
            Cooling factor for the temperature. It is used to reduce
            the temperature after each step. A value between 0 and
            1 is expected.
        penalty_factor:
            Factor to scale the penalty for infeasible solutions. It is used
            to penalize solutions that violate constraints, such as arrival
            times and deadlines. A higher value increases the penalty for
            infeasible solutions, making them less likely to be accepted.
            It is used to calculate the energy of the solution.
            It is used to calculate the makespan of the schedule.
            It is used to calculate the penalties for constraint violations.
        seed:
            Random seed for reproducible results. If None, random behavior
            will be non-deterministic.

    """

    def __init__(
        self,
        initial_temperature: float = 10000.0,
        steps: int = 10000,
        cool: float = 0.95,
        penalty_factor: int = 1_000_000,
        seed: int | None = None,
    ):
        self.initial_temperature = initial_temperature
        self.steps = steps
        self.cool = cool
        self.penalty_factor = penalty_factor
        self.seed = seed

    def solve(
        self,
        instance: JobShopInstance,
        initial_state: list[list[int]] | None = None,
    ) -> Schedule:
        """Solves the given Job Shop Scheduling problem using
        simulated annealing.

        Args:
            instance (JobShopInstance): The job shop problem instance to solve.
            initial_state (list[list[int]], optional): Initial job sequences
            for each machine. If None, a random initial state is generated.

        Returns:
            Schedule: The best schedule found for the given instance.

        Notes:
            - If a seed is set, the random state is saved and restored to
            ensure reproducibility.

            - The annealing process parameters (temperature, steps,
            cooling rate) are set from the solver's attributes.

        """
        # Save current random state and set new seed if provided
        if self.seed is not None:
            old_state = random.getstate()
            random.seed(self.seed)
        try:
            if initial_state is None:
                # Generate a random initial state if not provided
                initial_state = self._generate_initial_state(instance)
            annealer = JobShopAnnealer(
                instance, initial_state, penalty_factor=self.penalty_factor
            )
            annealer.Tmax = self.initial_temperature
            annealer.steps = self.steps
            annealer.cool = self.cool
            annealer.copy_strategy = "deepcopy"

            best_state, _ = annealer.anneal()
            return Schedule.from_job_sequences(instance, best_state)
        finally:
            # Restore the previous random state
            if self.seed is not None:
                random.setstate(old_state)

    def _generate_initial_state(
        self, instance: JobShopInstance
    ) -> list[list[int]]:
        """Generates deadline-aware initial sequences for each machine."""
        state: list[list[int]] = [[] for _ in range(instance.num_machines)]
        job_progress = [0 for _ in range(instance.num_jobs)]

        # Create list of jobs sorted by earliest deadline first
        # Handle None deadlines by treating them as infinite
        # (very large number)
        jobs_by_deadline = sorted(
            range(instance.num_jobs),
            key=lambda j: (
                float(instance.jobs[j][-1].deadline)
                if instance.jobs[j][-1].deadline is not None
                else float("inf")
            ),
        )

        # Schedule operations while respecting job order constraints
        while any(
            job_progress[j] < len(instance.jobs[j])
            for j in range(instance.num_jobs)
        ):
            for job_id in jobs_by_deadline:
                # Check if this job has more operations to schedule
                if job_progress[job_id] < len(instance.jobs[job_id]):
                    operation = instance.jobs[job_id][job_progress[job_id]]
                    machine_id = (
                        operation.machines[0]
                        if isinstance(operation.machines, list)
                        else operation.machines
                    )
                    state[machine_id].append(job_id)
                    job_progress[job_id] += 1

        return state
