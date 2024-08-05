"""Constants for the graph module."""

import enum


class EdgeType(enum.Enum):
    """Enumeration of edge types."""

    CONJUNCTIVE = 0
    DISJUNCTIVE = 1


class NodeType(enum.Enum):
    """Enumeration of node types.

    Nodes of type :class:`NodeType.OPERATION`, :class:`NodeType.MACHINE`, and
    :class:`NodeType.JOB` have specific attributes associated with them in the
    :class:`Node` class.

    On the other hand, Nodes of type :class:`NodeType.GLOBAL`,
    :class:`NodeType.SOURCE`, and :class:`NodeType.SINK` are used to represent
    different concepts in the graph and accesing them, but they do not have
    specific attributes associated with them.

    .. tip::

        While uncommon, it can be useful to extend this enumeration with
        additional node types. This can be achieved using
        `aenum <https://github.com/ethanfurman/aenum>`_'s
        ``extend_enum`` (requires using Python 3.11+).
    """

    OPERATION = enum.auto()
    MACHINE = enum.auto()
    JOB = enum.auto()
    GLOBAL = enum.auto()
    SOURCE = enum.auto()
    SINK = enum.auto()
