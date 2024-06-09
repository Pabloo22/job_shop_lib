"""Exceptions for the job shop scheduling library."""


class JobShopLibError(Exception):
    """Base class for exceptions in the job shop scheduling library.

    This class is the base class for all exceptions raised by the job
    shop scheduling library.

    It is useful for catching any exception that is raised by the
    library, without having to catch each specific exception
    separately.
    """


class NoSolutionFoundError(JobShopLibError):
    """Exception raised when no solution is found by a solver.

    This exception is raised by a solver when it is unable to find a
    feasible solution within a given time limit.

    It is useful to distinguish this exception from other exceptions
    that may be raised by a solver, such as a ValueError or a
    TypeError, which may indicate a bug in the code or an invalid
    input, rather than a failure to find a solution.
    """


class ValidationError(JobShopLibError):
    """Exception raised when a validation check fails.

    This exception is raised when a validation check fails, indicating
    that the input data is invalid or does not meet the requirements of
    the function or class that is performing the validation.

    It is useful to distinguish this exception from other exceptions
    that may be raised by a function or class, such as a ValueError or
    a TypeError, which may indicate a bug in the code or an invalid
    input, rather than a validation failure.
    """


class UninitializedAttributeError(JobShopLibError):
    """Exception raised when an attribute is accessed before initialization."""
