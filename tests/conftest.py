import pytest
from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.reinforcement_learning import (
    MakespanReward,
    IdleTimeReward,
    SingleJobShopGraphEnv,
    MultiJobShopGraphEnv,
)
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserverConfig,
    FeatureObserverType,
    FeatureType,
)
from job_shop_lib.generation import GeneralInstanceGenerator
from job_shop_lib.graphs import build_disjunctive_graph, build_agent_task_graph
from job_shop_lib.benchmarking import load_benchmark_instance


@pytest.fixture
def job_shop_instance():
    jobs = [
        [Operation(0, 10), Operation(1, 20)],
        [Operation(1, 15), Operation(2, 10)],
    ]
    instance = JobShopInstance(jobs, "TestInstance")
    return instance


@pytest.fixture
def example_job_shop_instance():
    m1 = 0
    m2 = 1
    m3 = 2

    job_1 = [Operation(m1, 1), Operation(m2, 1), Operation(m3, 7)]
    job_2 = [Operation(m2, 5), Operation(m3, 1), Operation(m1, 1)]
    job_3 = [Operation(m3, 1), Operation(m1, 3), Operation(m2, 2)]

    jobs = [job_1, job_2, job_3]

    instance = JobShopInstance(
        jobs,
        name="Example",
        lower_bound=7,
    )
    return instance


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
def single_job_shop_graph_env_ft06() -> SingleJobShopGraphEnv:
    instance = load_benchmark_instance("ft06")
    job_shop_graph = build_disjunctive_graph(instance)
    feature_observer_configs = [
        FeatureObserverConfig(
            FeatureObserverType.IS_READY,
            kwargs={"feature_types": [FeatureType.JOBS]},
        )
    ]

    env = SingleJobShopGraphEnv(
        job_shop_graph=job_shop_graph,
        feature_observer_configs=feature_observer_configs,
        reward_function_type=MakespanReward,
        render_mode="save_video",
        render_config={"video_config": {"fps": 4}},
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
        FeatureObserverConfig(
            FeatureObserverType.IS_READY,
            kwargs={"feature_types": [FeatureType.JOBS]},
        )
    ]

    env = MultiJobShopGraphEnv(
        instance_generator=generator,
        feature_observer_configs=feature_observer_configs,
        graph_builder=build_agent_task_graph,
        reward_function_type=IdleTimeReward,
        render_mode="human",
        render_config={"video_config": {"fps": 4}},
    )

    return env
