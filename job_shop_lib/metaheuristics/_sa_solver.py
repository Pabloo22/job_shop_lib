import random
from job_shop_lib import BaseSolver, JobShopInstance, Schedule
from job_shop_lib.metaheuristics import JobShopAnnealer


class SimulatedAnnealingSolver(BaseSolver):
    """Simulated Annealing Solver for Job Shop Scheduling."""

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

    def solve(self, instance: JobShopInstance) -> Schedule:
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
