import pytest
import random

from job_shop_lib import (
    JobShopInstance,
    Operation,
    Schedule,
    ScheduledOperation,
)
from job_shop_lib.dispatching.rules import DispatchingRuleSolver
from job_shop_lib.reinforcement_learning import (
    SingleJobShopGraphEnv,
    MultiJobShopGraphEnv,
)
from job_shop_lib.dispatching import DispatcherObserverConfig, Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserverType,
    FeatureType,
)
from job_shop_lib.generation import GeneralInstanceGenerator
from job_shop_lib.graphs import (
    add_disjunctive_edges,
    add_conjunctive_edges,
    build_resource_task_graph,
    JobShopGraph,
)
from job_shop_lib.benchmarking import load_benchmark_instance


@pytest.fixture(name="job_shop_instance")
def job_shop_instance_fixture():
    jobs = [
        [Operation(0, 10), Operation(1, 20)],
        [Operation(1, 15), Operation(2, 10)],
    ]
    instance = JobShopInstance(jobs, "TestInstance")
    return instance


@pytest.fixture(name="job_shop_instance_with_extras")
def job_shop_instance_with_extras_fixture():
    jobs = [
        [
            Operation(0, 10, release_date=0, deadline=100, due_date=80),
            Operation(1, 20, release_date=10, deadline=110, due_date=90),
        ],
        [
            Operation(1, 15, release_date=5, deadline=105, due_date=85),
            Operation(2, 10, release_date=15, deadline=115, due_date=95),
        ],
    ]
    instance = JobShopInstance(jobs, "TestInstanceWithExtras")
    return instance


@pytest.fixture
def example_job_shop_instance():
    m0 = 0
    m1 = 1
    m2 = 2

    job_0 = [Operation(m0, 1), Operation(m1, 1), Operation(m2, 7)]
    job_1 = [Operation(m1, 5), Operation(m2, 1), Operation(m0, 1)]
    job_2 = [Operation(m2, 1), Operation(m0, 3), Operation(m1, 2)]

    jobs = [job_0, job_1, job_2]

    instance = JobShopInstance(
        jobs,
        name="Example",
        lower_bound=7,
    )
    return instance


@pytest.fixture
def dispatcher(  # pylint: disable=redefined-outer-name
    example_job_shop_instance: JobShopInstance,
) -> Dispatcher:
    """Provides a Dispatcher instance for the example_job_shop_instance."""
    return Dispatcher(example_job_shop_instance)


@pytest.fixture
def dispatcher_with_extras(
    job_shop_instance_with_extras: JobShopInstance,
) -> Dispatcher:
    """Provides a Dispatcher for an instance with release/due dates."""
    return Dispatcher(job_shop_instance_with_extras)


@pytest.fixture
def example_2_job_shop_instance():
    # Cada máquina se representa con un id (empezando por 0)
    m0 = 0
    m1 = 1
    m2 = 2

    j0 = [
        Operation(m0, duration=2),
        Operation(m1, duration=2),
        Operation(m2, duration=2),
    ]
    j1 = [
        Operation(m0, duration=1),
        Operation(m1, duration=1),
        Operation(m2, duration=1),
    ]
    j2 = [
        Operation(m0, duration=2),
        Operation(m2, duration=3),
        Operation(m1, duration=3),
    ]
    return JobShopInstance([j0, j1, j2], name="Example 2")


@pytest.fixture
def irregular_job_shop_instance():
    m1 = 0
    m2 = 1
    m3 = 2

    job_1 = [
        Operation(m1, 1),
        Operation(m2, 1),
        Operation(m3, 7),
        Operation(m1, 2),
    ]
    job_2 = [Operation(m2, 5), Operation(m3, 1), Operation(m1, 1)]
    job_3 = [Operation(m3, 1), Operation(m1, 3), Operation(m2, 2)]

    jobs = [job_1, job_2, job_3]

    instance = JobShopInstance(
        jobs,
        name="Irregular",
    )
    return instance


@pytest.fixture
def flexible_job_shop_instance2x2():
    """Create a simple job shop instance for testing."""
    jobs = [
        [
            Operation(machines=[0, 1], duration=3),
            Operation(machines=[0, 1], duration=2),
        ],
        [
            Operation(machines=[0, 1], duration=4),
            Operation(machines=[0, 1], duration=1),
        ],
    ]
    return JobShopInstance(jobs, name="test_instance")


@pytest.fixture
def single_job_shop_graph_env_ft06() -> SingleJobShopGraphEnv:
    instance = load_benchmark_instance("ft06")
    job_shop_graph = JobShopGraph(instance)
    add_disjunctive_edges(job_shop_graph)
    add_conjunctive_edges(job_shop_graph)

    feature_observer_configs = [
        DispatcherObserverConfig(
            FeatureObserverType.IS_READY,
            kwargs={"feature_types": [FeatureType.JOBS]},
        )
    ]

    env = SingleJobShopGraphEnv(
        job_shop_graph=job_shop_graph,
        feature_observer_configs=feature_observer_configs,
        render_mode="save_video",
        render_config={"video_config": {"fps": 4}},
    )
    return env


@pytest.fixture
def single_job_shop_graph_env_ft06_resource_task() -> SingleJobShopGraphEnv:
    instance = load_benchmark_instance("ft06")
    job_shop_graph = build_resource_task_graph(instance)
    feature_observer_configs = [
        DispatcherObserverConfig(
            FeatureObserverType.IS_READY,
            kwargs={"feature_types": [FeatureType.JOBS]},
        )
    ]

    env = SingleJobShopGraphEnv(
        job_shop_graph=job_shop_graph,
        feature_observer_configs=feature_observer_configs,
        render_mode="save_video",
        render_config={"video_config": {"fps": 4}},
    )
    return env


@pytest.fixture
def single_env_ft06_resource_task_graph_with_all_features() -> (
    SingleJobShopGraphEnv
):
    instance = load_benchmark_instance("ft06")
    job_shop_graph = build_resource_task_graph(instance)
    feature_observer_configs = [
        FeatureObserverType.DURATION,
        FeatureObserverType.EARLIEST_START_TIME,
        FeatureObserverType.IS_COMPLETED,
        FeatureObserverType.IS_SCHEDULED,
        FeatureObserverType.POSITION_IN_JOB,
        FeatureObserverType.REMAINING_OPERATIONS,
    ]

    env = SingleJobShopGraphEnv(
        job_shop_graph=job_shop_graph,
        feature_observer_configs=feature_observer_configs,
        render_mode="save_video",
        render_config={"video_config": {"fps": 4}},
        ready_operations_filter=None,
    )
    return env


@pytest.fixture
def multi_job_shop_graph_env() -> MultiJobShopGraphEnv:
    generator = GeneralInstanceGenerator(
        num_jobs=(3, 6),
        num_machines=(3, 5),
        allow_less_jobs_than_machines=False,
    )
    feature_observer_configs = [
        DispatcherObserverConfig(
            FeatureObserverType.IS_READY,
            kwargs={"feature_types": [FeatureType.JOBS]},
        )
    ]

    env = MultiJobShopGraphEnv(
        instance_generator=generator,
        feature_observer_configs=feature_observer_configs,
        graph_initializer=build_resource_task_graph,
        render_mode="human",
        render_config={"video_config": {"fps": 4}},
    )

    return env


@pytest.fixture
def example_schedule(  # W0621 = redefined-outer-name
    example_job_shop_instance: JobShopInstance,  # pylint: disable=W0621
) -> Schedule:
    """Creates a simple schedule for testing using DispatchingRuleSolver."""
    instance = example_job_shop_instance
    solver = DispatchingRuleSolver()
    schedule = solver.solve(instance)
    return schedule


@pytest.fixture
def instance_with_recirculation() -> JobShopInstance:
    """Create a job shop instance with recirculation."""
    m0 = 0
    m1 = 1
    m2 = 2

    job_0 = [Operation(m0, 1), Operation(m1, 1), Operation(m0, 7)]
    job_1 = [Operation(m1, 5), Operation(m2, 1), Operation(m1, 1)]
    job_2 = [Operation(m2, 1), Operation(m0, 3), Operation(m1, 2)]

    jobs = [job_0, job_1, job_2]

    instance = JobShopInstance(
        jobs,
        name="Recirculation",
    )
    return instance


@pytest.fixture
def minimal_infeasible_instance():
    """Creates a minimal instance that's infeasible with tight constraints."""
    jobs = [
        [Operation(0, 10)],  # Operation takes 10 time units
        [Operation(0, 10)],  # Another operation on same machine
    ]
    return JobShopInstance(jobs, name="MinimalInfeasible")


@pytest.fixture(name="complete_schedule")
def complete_schedule_fixture(job_shop_instance):
    schedule = Schedule(instance=job_shop_instance, check=True)
    operations = [
        ScheduledOperation(
            job_shop_instance.jobs[0][0], start_time=0, machine_id=0
        ),
        ScheduledOperation(
            job_shop_instance.jobs[0][1], start_time=0, machine_id=1
        ),
        ScheduledOperation(
            job_shop_instance.jobs[1][0], start_time=100, machine_id=1
        ),
        ScheduledOperation(
            job_shop_instance.jobs[1][1], start_time=100, machine_id=2
        ),
    ]
    for op in operations:
        schedule.add(op)
    return schedule


@pytest.fixture
def instance_with_release_dates_and_deadlines():
    jobs = [
        [
            Operation(machines=0, duration=3, release_date=2, deadline=10),
            Operation(machines=1, duration=2, release_date=3, deadline=8),
        ],
        [
            Operation(machines=0, duration=2, release_date=1, deadline=8),
            Operation(machines=1, duration=1, release_date=2, deadline=6),
        ],
    ]
    return JobShopInstance(jobs=jobs)


@pytest.fixture
def ft06_instance():
    """Load the ft06 benchmark instance."""
    return load_benchmark_instance("ft06")


@pytest.fixture
def seeded_rng() -> random.Random:
    return random.Random(42)


@pytest.fixture
def single_machine_instance() -> JobShopInstance:
    # Two single-op jobs on same machine
    jobs = [[Operation(0, 2)], [Operation(0, 3)]]
    return JobShopInstance(jobs, name="SingleMachine")


@pytest.fixture
def two_machines_instance() -> JobShopInstance:
    # Two jobs, each with one operation on different machines
    jobs = [[Operation(0, 5)], [Operation(1, 3)]]
    return JobShopInstance(jobs, name="TwoMachines")
