"""Contains factory functions for creating dispatching rules, machine choosers,
and pruning functions for the job shop scheduling problem.

The factory functions create and return the appropriate functions based on the
specified names or enums.
"""

from typing import TypeVar, Generic, Any, Dict

from dataclasses import dataclass, field

from job_shop_lib.exceptions import ValidationError


# Disable pylint's false positive
# pylint: disable=invalid-name
T = TypeVar("T")


@dataclass(frozen=True)
class DispatcherObserverConfig(Generic[T]):
    """Configuration for initializing any type of class.

    Useful for specifying the type of the
    :class:`~job_shop_lib.dispatching.DispatcherObserver` and additional
    keyword arguments to pass to the dispatcher observer constructor while
    not containing the ``dispatcher`` argument.

    Args:
        class_type:
            Type of the class to be initialized. It can be the class type, an
            enum value, or a string. This is useful for the creation of
            :class:`~job_shop_lib.dispatching.DispatcherObserver` instances
            from the factory functions.
        kwargs:
            Keyword arguments needed to initialize the class. It must not
            contain the ``dispatcher`` argument.

    .. seealso::

        - :class:`~job_shop_lib.dispatching.DispatcherObserver`
        - :func:`job_shop_lib.dispatching.feature_observers.\\
          feature_observer_factory`
    """

    # We use the type hint T, instead of ObserverType, to allow for string or
    # specific Enum values to be passed as the type argument. For example:
    # FeatureObserverConfig = DispatcherObserverConfig[
    #     Type[FeatureObserver] | FeatureObserverType | str
    # ]
    # This allows for the creation of a FeatureObserver instance
    # from the factory function.
    class_type: T
    """Type of the class to be initialized. It can be the class type, an
    enum value, or a string. This is useful for the creation of
    :class:`DispatcherObserver` instances from the factory functions."""

    kwargs: Dict[str, Any] = field(default_factory=dict)
    """Keyword arguments needed to initialize the class. It must not
    contain the ``dispatcher`` argument."""

    def __post_init__(self):
        if "dispatcher" in self.kwargs:
            raise ValidationError(
                "The 'dispatcher' argument should not be included in the "
                "kwargs attribute."
            )
