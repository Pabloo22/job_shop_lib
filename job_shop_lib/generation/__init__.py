"""Package for generating job shop instances.

.. autosummary::
    :nosignatures:

    InstanceGenerator
    GeneralInstanceGenerator
    modular_instance_generator
    generate_machine_matrix_with_recirculation
    generate_machine_matrix_without_recirculation
    generate_duration_matrix
    range_size_selector
    choice_size_selector
    get_default_machine_matrix_creator
    get_default_duration_matrix_creator
    ReleaseDateStrategy
    create_release_dates_matrix
    get_independent_release_date_strategy
    get_cumulative_release_date_strategy
    get_mixed_release_date_strategy
    compute_horizon_proxy

"""

from job_shop_lib.generation._size_selectors import (
    range_size_selector,
    choice_size_selector,
)
from job_shop_lib.generation._machine_matrix import (
    generate_machine_matrix_with_recirculation,
    generate_machine_matrix_without_recirculation,
    get_default_machine_matrix_creator,
)
from job_shop_lib.generation._duration_matrix import (
    get_default_duration_matrix_creator,
    generate_duration_matrix,
)
from job_shop_lib.generation._release_date_matrix import (
    ReleaseDateStrategy,
    create_release_dates_matrix,
    get_independent_release_date_strategy,
    get_cumulative_release_date_strategy,
    get_mixed_release_date_strategy,
    compute_horizon_proxy,
)
from job_shop_lib.generation._modular_instance_generator import (
    modular_instance_generator,
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
    "modular_instance_generator",
    "range_size_selector",
    "choice_size_selector",
    "get_default_machine_matrix_creator",
    "get_default_duration_matrix_creator",
    "ReleaseDateStrategy",
    "create_release_dates_matrix",
    "get_independent_release_date_strategy",
    "get_cumulative_release_date_strategy",
    "get_mixed_release_date_strategy",
    "compute_horizon_proxy",
]
