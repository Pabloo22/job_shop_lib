"""Package for generating job shop instances."""

from job_shop_lib.generation.instance_generator import InstanceGenerator
from job_shop_lib.generation.general_instance_generator import (
    GeneralInstanceGenerator,
)

__all__ = [
    "InstanceGenerator",
    "GeneralInstanceGenerator",
]
