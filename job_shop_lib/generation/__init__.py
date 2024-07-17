"""Package for generating job shop instances."""

from job_shop_lib.generation._instance_generator import InstanceGenerator
from job_shop_lib.generation._general_instance_generator import (
    GeneralInstanceGenerator,
)

__all__ = [
    "InstanceGenerator",
    "GeneralInstanceGenerator",
]
