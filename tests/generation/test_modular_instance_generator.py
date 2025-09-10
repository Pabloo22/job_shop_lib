from job_shop_lib.generation import (
    get_default_machine_matrix_creator,
    get_default_duration_matrix_creator,
    modular_instance_generator,
    range_size_selector,
)


def test_reproducibility():
    machine_matrix_gen = get_default_machine_matrix_creator(
        size_selector=range_size_selector,
        with_recirculation=False,
    )
    duration_matrix_gen = get_default_duration_matrix_creator(
        duration_range=(1, 10),
    )
    instance_gen1 = modular_instance_generator(
        machine_matrix_creator=machine_matrix_gen,
        duration_matrix_creator=duration_matrix_gen,
        seed=42,
    )
    instance_gen2 = modular_instance_generator(
        machine_matrix_creator=machine_matrix_gen,
        duration_matrix_creator=duration_matrix_gen,
        seed=42,
    )

    instance1 = next(instance_gen1)
    instance2 = next(instance_gen2)
    assert instance1 == instance2
    instance1 = next(instance_gen1)
    instance2 = next(instance_gen2)
    assert instance1 == instance2
    instance1 = next(instance_gen1)
    instance2 = next(instance_gen2)
