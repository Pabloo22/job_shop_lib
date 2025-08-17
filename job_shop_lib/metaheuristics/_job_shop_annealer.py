import random
import math
import time

import simanneal

from job_shop_lib import JobShopInstance, Schedule
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.metaheuristics import (
    NeighborGenerator,
    ObjectiveFunction,
    swap_in_critical_path,
    get_makespan_with_penalties_objective,
)


class JobShopAnnealer(simanneal.Annealer):
    """Helper class for the :class:`SimulatedAnnealingSolver`.

    It uses `simanneal <https://github.com/perrygeo/simanneal>`_ as the
    backend.

    In the context of the job shop scheduling problem, simulated annealing is
    particularly useful for improving previous solutions.

    The neighbor move is pluggable via a ``neighbor_generator`` function. By
    default it uses :func:`swap_in_critical_path`, but any function that takes
    a schedule and a random generator and returns a new schedule can be
    provided to tailor the exploration of the search space.

    The process involves iteratively exploring the solution space:

    1. A random move is made to alter the current state. This is done by
       swapping two operations in the sequence of a machine.
    2. The "energy" of the new state is evaluated using an objective function.
       With the default objective function, the energy is calculated as the
       makespan of the schedule plus penalties for any constraint violations
       (such as deadlines and due dates). See
       :func:`get_makespan_with_penalties_objective` for details. You can
       create custom objective functions by implementing the
       :class:`ObjectiveFunction` interface, which takes a schedule and returns
       a float representing the energy of that schedule.
    3. The new state is accepted if it has lower energy (a better solution).
       If it has higher energy, it might still be accepted with a certain
       probability, which depends on the current "temperature". The
       temperature decreases over time, reducing the chance of accepting
       worse solutions as the algorithm progresses. This helps to avoid
       getting stuck in local optima.

    This is repeated until the solution converges or a maximum number of
    steps is reached.

    Tuning the annealer is crucial for performance. The base
    ``simanneal.Annealer`` class provides parameters that can be adjusted:

    - ``Tmax``: Maximum (starting) temperature (default: 25000.0).
    - ``Tmin``: Minimum (ending) temperature (default: 2.5).
    - ``steps``: Number of iterations (default: 50000).
    - ``updates``: Number of progress updates (default: 100).

    A good starting point is to set ``Tmax`` to a value that accepts about 98%
    of moves and ``Tmin`` to a value where the solution no longer improves.
    The number of ``steps`` should be large enough to explore the search space
    thoroughly.

    These parameters can be set on the annealer instance. For example:
    ``annealer.Tmax = 12000.0``

    Alternatively, this class provides an ``auto`` method to find reasonable
    parameters based on a desired runtime:
    ``auto_schedule = annealer.auto(minutes=1)``
    ``annealer.set_schedule(auto_schedule)``

    Attributes:
        instance:
            The job shop instance to solve.
        random_generator:
            Random generator for reproducibility.
        neighbor_generator:
            Function used to generate neighbors from the current schedule.
            Defaults to :func:`swap_in_critical_path`.
        objective_function:
            Function that computes the energy of the schedule. If ``None``,
            it defaults to :func:`get_makespan_with_penalties_objective`.
            This function receives a schedule and returns the energy that will
            be minimized by the annealer.

    Args:
        instance:
            The job shop instance to solve. It retrieves the jobs and
            machines from the instance and uses them to create the schedule.
        initial_state:
            Initial state of the schedule as a list of lists, where each
            sublist represents the operations of a job.
        seed:
            Random seed for reproducibility. If ``None``, random behavior
            will be non-deterministic.
        neighbor_generator:
            Function that receives the current schedule and a random generator
            and returns a new schedule to explore. Defaults to
            :func:`swap_in_critical_path`. Use this to plug in custom
            neighborhoods (e.g., adjacent swaps).
        objective_function:
            Function that computes the energy of the schedule. If ``None``,
            it defaults to :func:`get_makespan_with_penalties_objective`.
            This callable receives a :class:`~job_shop_lib.Schedule` and
            returns a float that will be minimized by the annealer.
    """

    copy_strategy = "method"

    def __init__(
        self,
        instance: JobShopInstance,
        initial_state: Schedule,
        *,
        seed: int | None = None,
        neighbor_generator: NeighborGenerator = swap_in_critical_path,
        objective_function: ObjectiveFunction | None = None,
    ):
        super().__init__(initial_state)
        self.instance = instance
        if objective_function is None:
            self.objective_function = get_makespan_with_penalties_objective()
        else:
            self.objective_function = objective_function
        self.random_generator = random.Random(seed)
        self.neighbor_generator = neighbor_generator

    def _get_state(self) -> Schedule:
        """Returns the current state of the annealer.

        This method facilitates type checking.
        """
        return self.state

    def move(self) -> None:
        """Generates a neighbor state using the configured neighbor generator.

        Delegates to ``self.neighbor_generator`` with the current schedule and
        the internal random generator, enabling pluggable neighborhoods.
        """
        self.state = self.neighbor_generator(
            self._get_state(), self.random_generator
        )

    def anneal(self) -> tuple[Schedule, float]:
        """Minimizes the energy of a system by simulated annealing.

        Overrides the ``anneal`` method from the base class to use the
        random  generator defined in the constructor.

        Returns:
            The best state and energy found during the annealing process.
        """
        step = 0
        self.start = time.time()

        # Precompute factor for exponential cooling from Tmax to Tmin
        if self.Tmin <= 0.0:
            raise ValidationError(
                "Exponential cooling requires a minimum "
                "temperature greater than zero."
            )
        t_factor = -math.log(self.Tmax / self.Tmin)

        # Note initial state
        t = self.Tmax
        current_energy = self.energy()
        prev_state = self.copy_state(self.state)
        prev_energy = current_energy
        self.best_state = self.copy_state(self.state)
        self.best_energy = current_energy
        trials, accepts, improves = 0, 0, 0
        update_wave_length = 0  # not used, but avoids pylint warning
        if self.updates > 0:
            update_wave_length = self.steps / self.updates
            self.update(step, t, current_energy, None, None)

        # Attempt moves to new states
        while step < self.steps and not self.user_exit:
            step += 1
            t = self.Tmax * math.exp(t_factor * step / self.steps)
            self.move()
            current_energy = self.energy()
            delta_e = current_energy - prev_energy
            trials += 1
            if (
                delta_e > 0.0
                and math.exp(-delta_e / t) < self.random_generator.random()
            ):
                # Restore previous state
                self.state = self.copy_state(prev_state)
                current_energy = prev_energy
            else:
                # Accept new state and compare to best state
                accepts += 1
                if delta_e < 0.0:
                    improves += 1
                prev_state = self.copy_state(self.state)
                prev_energy = current_energy
                if current_energy < self.best_energy:
                    self.best_state = self.copy_state(self.state)
                    self.best_energy = current_energy
            if self.updates < 1:
                continue
            if (step // update_wave_length) > (
                (step - 1) // update_wave_length
            ):
                self.update(
                    step,
                    t,
                    current_energy,
                    accepts / trials,
                    improves / trials,
                )
                trials, accepts, improves = 0, 0, 0

        self.state = self.copy_state(self.best_state)
        if self.save_state_on_exit:
            self.save_state()

        return self.best_state, self.best_energy

    def energy(self) -> float:
        """Computes the energy of the current schedule using the objective
        function provided."""
        schedule = self._get_state()
        return self.objective_function(schedule)
