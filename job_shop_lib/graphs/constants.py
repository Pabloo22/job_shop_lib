"""Constants for the graph module."""

import enum


class EdgeType(enum.Enum):
    """Enumeration of edge types."""

    CONJUNCTIVE = 0
    DISJUNCTIVE = 1


class NodeType(enum.Enum):
    """Enumeration of node types."""

    OPERATION = enum.auto()
    MACHINE = enum.auto()
    JOB = enum.auto()
    GLOBAL = enum.auto()
    SOURCE = enum.auto()
    SINK = enum.auto()
