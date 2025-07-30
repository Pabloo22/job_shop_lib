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

    """

    def __init__(
        self,
        initial_temperature: float = 10000.0,
        steps: int = 10000,
        cool: float = 0.95,
        penalty_factor: int = 1_000_000,
    ):
        self.initial_temperature = initial_temperature
        self.steps = steps
        self.cool = cool
        self.penalty_factor = penalty_factor

    def solve(
        self,
        instance: JobShopInstance,
        initial_state: list[list[int]] | None = None,
    ) -> Schedule:
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

    def _generate_initial_state(
        self, instance: JobShopInstance
    ) -> list[list[int]]:
        """Generates random initial sequences for each machine."""
        state = []
        for machine_id in range(instance.num_machines):
            job_ids = []
            for job_id, job in enumerate(instance.jobs):
                for operation in job:
                    if machine_id in operation.machines:
                        job_ids.append(job_id)
            random.shuffle(job_ids)
            state.append(job_ids)
        return state
