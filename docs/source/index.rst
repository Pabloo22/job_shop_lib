.. JobShopLib documentation master file, created by
   sphinx-quickstart on Sun Jul  7 16:51:14 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

JobShopLib
======================================
**Version:** |version|

.. image:: https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png
   :target: https://github.com/Pabloo22/job_shop_lib
   :width: 24px
   :alt: GitHub
   :align: right

.. image:: examples/output/ft06_optimized.gif
    :alt: JobShopLib example gif
    :align: center

JobShopLib is a Python package for **creating**, **solving**, and **visualizing**
job shop scheduling problems.

It provides solvers based on:

- **Graph neural networks** (Gymnasium environment)
- **Dispatching rules**
- **Simulated annealing**
- **Constraint programming** (CP-SAT from Google OR-Tools)

It also includes utilities for:

- **Load benchmark instances**
- **Generating random problems**
- **Gantt charts**
- **Disjunctive graphs** (and any variant)
- Training a GNN-based dispatcher using **reinforcement learning** or **imitation learning**

JobShopLib's design is intended to be modular and easy-to-use:

.. code-block:: python

    import matplotlib.pyplot as plt
    plt.style.use("ggplot")

    from job_shop_lib import JobShopInstance, Operation
    from job_shop_lib.benchmarking import load_benchmark_instance
    from job_shop_lib.generation import GeneralInstanceGenerator
    from job_shop_lib.constraint_programming import ORToolsSolver
    from job_shop_lib.visualization import plot_gantt_chart, create_gif, plot_gantt_chart_wrapper
    from job_shop_lib.dispatching import DispatchingRuleSolver

    # Create your own instance manually,
    job_1 = [Operation(machines=0, duration=1), Operation(1, 1), Operation(2, 7)]
    job_2 = [Operation(1, 5), Operation(2, 1), Operation(0, 1)]
    job_3 = [Operation(2, 1), Operation(0, 3), Operation(1, 2)]
    jobs = [job_1, job_2, job_3]
    instance = JobShopInstance(jobs)

    # load a popular benchmark instance,
    ft06 = load_benchmark_instance("ft06")

    # or generate a random one.
    generator = GeneralInstanceGenerator(
        duration_range=(5, 10), seed=42, num_jobs=5, num_machines=5
    )
    random_instance = generator.generate()

    # Solve it using constraint programming,
    solver = ORToolsSolver(max_time_in_seconds=10)
    ft06_schedule = solver(ft06)

    # Visualize the solution as a Gantt chart,
    fig, ax = plot_gantt_chart(ft06_schedule)
    plt.show()

    # or visualize how the solution is built step by step using a dispatching rule.
    mwkr_solver = DispatchingRuleSolver("most_work_remaining")
    plt.style.use("ggplot")
    plot_function = plot_gantt_chart_wrapper(
        title="Solution with Most Work Remaining Rule"
    )
    create_gif(  # Creates the gif above
        gif_path="ft06_optimized.gif",
        instance=ft06,
        solver=mwkr_solver,
        plot_function=plot_function,
        fps=4,
    )

See
`this <https://colab.research.google.com/drive/1XV_Rvq1F2ns6DFG8uNj66q_rcowwTZ4H?usp=sharing>`__
Google Colab notebook for a quick start guide!

Installing
-----------

.. code-block:: bash

    pip install job_shop_lib

Contents
--------

.. toctree::
    :maxdepth: 1

    install
    tutorial
    examples
    api