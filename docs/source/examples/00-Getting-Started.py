"""
Getting Started to Job Shop Lib
===============================

The main class of the library is the ``JobShopInstance`` class, which
stores a list of jobs and its ``Operations``.

Each operation is also a class, which stores the machine(s) in which the
operation can be processed and its duration (also known as processing
time). Let’s see an example of how to use the ``JobShopInstance`` class
to model a JSSP instance.

In this example, we model a simple Job Shop Scheduling Problem using the
``JobShopInstance`` class. We define three types of machines: CPU, GPU,
and Data Center, each represented by a unique identifier.

"""

from job_shop_lib import JobShopInstance, Operation

CPU = 0
GPU = 1
DATA_CENTER = 2

job_1 = [Operation(CPU, 1), Operation(GPU, 1), Operation(DATA_CENTER, 7)]
job_2 = [Operation(GPU, 5), Operation(DATA_CENTER, 1), Operation(CPU, 1)]
job_3 = [Operation(DATA_CENTER, 1), Operation(CPU, 3), Operation(GPU, 2)]

jobs = [job_1, job_2, job_3]

instance = JobShopInstance(
    jobs,
    name="Example",
    # Any extra parameters are stored inside the
    # metadata attribute as a dictionary:
    lower_bound=7,
)
instance


# %%
# The job and its position in it are automatically inferred. Now, we can
# access to some stats of the instance:
# 

print("Number of jobs:", instance.num_jobs)
print("Number of machines:", instance.num_machines)
print("Number of operations:", instance.num_operations)
print("Name:", instance.name)
print("Is flexible?:", instance.is_flexible)
print("Max operation time:", instance.max_duration)
print("Machine loads:", instance.machine_loads)

import numpy as np

np.array(instance.durations_matrix)

np.array(instance.machines_matrix)


# %%
# Some of this attributes could take :math:`O(num\_operations)` to
# compute. This is the reason we use the ``functools.cached_property``
# decorator to cache the results of the computation of these attributes.
# 


# %%
# Note that we just had to specify the machines in which the operation can
# be processed and its duration. The ``job_id`` and the position of the
# operation in the job are automatically inferred by the
# ``JobShopInstance`` class.
# 

first_operation = job_1[0]
print("Machine id:", first_operation.machine_id)
print("Duration:", first_operation.duration)
# If the operation only has one machine, we can use the `machine_id` property
# instead of the `machines` attribute:
print("Job id:", first_operation.job_id)
print("Position:", first_operation.position_in_job)
print("Operation id:", first_operation.operation_id)
print("String representation:", str(first_operation))