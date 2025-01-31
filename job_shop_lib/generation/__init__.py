"""Package for generating job shop instances."""

from job_shop_lib.generation._utils import (
    generate_duration_matrix,
    generate_machine_matrix_with_recirculation,
    generate_machine_matrix_without_recirculation,
)
from job_shop_lib.generation._instance_generator import InstanceGenerator
from job_shop_lib.generation._general_instance_generator import (
    GeneralInstanceGenerator,
)

__all__ = [
    "InstanceGenerator",
    "GeneralInstanceGenerator",
    "generate_duration_matrix",
    "generate_machine_matrix_with_recirculation",
    "generate_machine_matrix_without_recirculation",
]
