import pytest
from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.metaheuristics import JobShopAnnealer
from job_shop_lib.metaheuristics._simulated_annealing_solver import (
    SimulatedAnnealingSolver,
)
from job_shop_lib import Schedule


# Fixture for a simple job shop instance
@pytest.fixture
def simple_instance():
    jobs = [
        [
            Operation(machines=0, duration=3),
            Operation(machines=1, duration=2),
        ],
        [
            Operation(machines=0, duration=2),
            Operation(machines=1, duration=1),
        ],
    ]
    return JobShopInstance(jobs=jobs)


# Fixture for ft06 instance
@pytest.fixture
def ft06_instance():
    jobs = []
    with open("ft06.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()[4:]  # Skip header
        num_jobs, num_machines = map(int, lines[0].split())
        for job_id in range(num_jobs):
            operations = []
            data = lines[job_id + 1].split()
            for op_idx in range(num_machines):
                machine_id = int(data[2 * op_idx])
                duration = int(data[2 * op_idx + 1])
                operations.append(
                    Operation(
                        machines=machine_id,
                        duration=duration,
                    )
                )
            jobs.append(operations)
    return JobShopInstance(jobs=jobs)


# Basic Functionality Test
def test_basic_functionality(simple_instance):
    solver = SimulatedAnnealingSolver(
        initial_temperature=100, steps=100, cool=0.95
    )
    schedule = solver.solve(simple_instance)

    assert isinstance(schedule, Schedule)
    assert schedule.instance == simple_instance
    assert len(schedule.schedule) == simple_instance.num_machines

    # Check that all operations are scheduled
    scheduled_ops = sum(len(m) for m in schedule.schedule)
    total_ops = sum(len(job) for job in simple_instance.jobs)
    assert scheduled_ops == total_ops


# Initialization Test
def test_initialization(simple_instance):
    # Create a custom initial state
    initial_state = [
        [0, 1],  # Machine 0: Job0 then Job1
        [0, 1],  # Machine 1: Job0 then Job1
    ]

    annealer = JobShopAnnealer(
        simple_instance, initial_state, penalty_factor=1_000_000
    )

    assert annealer.state == initial_state


# Arrival Times constraint test
def test_arrival_times_constraint(simple_instance):
    # Set arrival times for jobs
    simple_instance.arrival_times = [2, 3]  # Job0 arrives at t=2, Job1 at t=3

    solver = SimulatedAnnealingSolver(
        initial_temperature=1000,
        steps=5000,
        cool=0.95,
        penalty_factor=1_000_000,
    )
    schedule = solver.solve(simple_instance)

    # Check first operation of each job starts after arrival time
    for job_id, job in enumerate(simple_instance.jobs):
        first_op = job[0]
        scheduled_op = next(
            op
            for machine_schedule in schedule.schedule
            for op in machine_schedule
            if op.operation == first_op
        )
        assert scheduled_op.start_time >= simple_instance.arrival_times[job_id]


# Deadlines constraint test
def test_deadlines_constraint(simple_instance):
    # Set deadlines for jobs
    simple_instance.deadlines = [10, 8]  # Job0 deadline=10, Job1 deadline=8

    solver = SimulatedAnnealingSolver(
        initial_temperature=1000,
        steps=5000,
        cool=0.95,
        penalty_factor=1_000_000,
    )
    schedule = solver.solve(simple_instance)

    # Check last operation of each job completes before deadline
    for job_id, job in enumerate(simple_instance.jobs):
        last_op = job[-1]
        scheduled_op = next(
            op
            for machine_schedule in schedule.schedule
            for op in machine_schedule
            if op.operation == last_op
        )
        completion_time = scheduled_op.start_time + last_op.duration
        assert completion_time <= simple_instance.deadlines[job_id]


# Import test
def test_import():
    from job_shop_lib.metaheuristics import JobShopAnnealer

    assert JobShopAnnealer is not None


# Solution quality test of ft06 instance
def test_solution_quality(ft06_instance):
    solver = SimulatedAnnealingSolver(
        initial_temperature=10_000,
        steps=50_000,
        cool=0.99,
        penalty_factor=1_000_000,
    )

    schedule = solver.solve(ft06_instance)
    makespan = schedule.makespan()

    # Known optimal makespan for ft06 is 55
    # Allow some suboptimality due to stochastic nature
    assert makespan <= 60  # Within 10% of optimal
    print(f"\nft06 makespan: {makespan} (optimal=55)")
