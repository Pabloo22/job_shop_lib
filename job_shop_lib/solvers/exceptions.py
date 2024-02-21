class NoSolutionFound(ValueError):
    """Exception raised when no solution is found by a solver.

    This exception is raised by a solver when it is unable to find a
    feasible solution within a given time limit.

    It is useful to distinguish this exception from other exceptions
    that may be raised by a solver, such as a ValueError or a
    TypeError, which may indicate a bug in the code or an invalid
    input, rather than a failure to find a solution.

    It inherits from ValueError, so it can be caught by the same
    exception handling code that catches ValueError.
    """
