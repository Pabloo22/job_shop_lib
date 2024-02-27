# job_shop_lib
[![Tests](https://github.com/Pabloo22/job_shop_lib/actions/workflows/tests.yaml/badge.svg)](https://github.com/Pabloo22/job_shop_lib/actions/workflows/tests.yaml)
![Python 3.11](https://img.shields.io/badge/python-3.11-3776AB)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<img src="logo_with_transparent_background.png" alt="Job Shop Lib" width="150">


A framework to model and solve the Job Shop Scheduling Problem with a special focus on graph representations.

## Example
```python
import matplotlib.pyplot as plt

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.solvers import CPSolver
from job_shop_lib.visualization import plot_gantt_chart

MACHINE_1 = 0
MACHINE_2 = 1
MACHINE_3 = 2

job_1 = [Operation(MACHINE_1, 1), Operation(MACHINE_2, 1), Operation(MACHINE_3, 7)]
job_2 = [Operation(MACHINE_2, 5), Operation(MACHINE_3, 1), Operation(MACHINE_1, 1)]
job_3 = [Operation(MACHINE_3, 1), Operation(MACHINE_1, 3), Operation(MACHINE_2, 2)]

jobs = [job_1, job_2, job_3]

instance = JobShopInstance(jobs, name="Example")

cp_sat_solver = CPSolver()
schedule = cp_sat_solver(instance)

fig, ax = plot_gantt_chart(schedule)
plt.show()
```
![Example Gannt Chart](example_gantt_chart.png)

For more details, check the [tutorial](tutorial) folder.

## Installation

In the future, the library will be available on PyPI. For now, you can install it from the source code.

1. Clone the repository.

2. Install [poetry](https://python-poetry.org/docs/) if you don't have it already:
```bash
pip install poetry==1.7
```
3. Create the virtual environment:
```bash
poetry shell
```
4. Install dependencies:
```bash
poetry install --with notebooks --with test --with lint
```
or equivalently:
```bash
make poetry_install_all 
```
